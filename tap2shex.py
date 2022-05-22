from jinja2 import Template
import streamlit as st
from streamlit_toy_dict_input import dict_input
from pyshexc.parser_impl.generate_shexj import parse
import json

PIXELS_PER_LINE = 27
INDENT = 8

st.title('DCTAP JSON to ShExC')
st.write('**Convert DCTAP JSON to ShExC using Jinja Template**')


ap_template = {
	"namespaces": {
		"ex": "http://ex.example/#",
		"xsd": "http://www.w3.org/2001/XMLSchema#",
		"school": "http://school.example/#",
		"foaf": "http://xmlns.com/foaf/0.1/"
	},
	"shapes": [
		{
			"shapeID": "school:Enrollee",
			"statement_templates": [
				{
					"propertyID": "ex:hasGuardian",
					"valueNodeType": "iri",
					"min": "1",
					"max": "2",
				},
				{
					"propertyID": "foaf:age",
					"valueDataType": "xsd:integer",
					"MinInclusive": "13",
					"MaxInclusive": "20",
				}
			]
		}
	]
}

st.subheader('1. DCTAP Python Dictionary')

ap_dict = dict_input("Edit to alter the dictionary", ap_template)

st.subheader('2. DCTAP JSON')
st.json(ap_dict)

shex_jinja_default = """
{%- for prefix, uri in namespaces.items() %}
PREFIX {{prefix}}: <{{uri}}>
{%- endfor %}
BASE <http://purl.org/yama/example/mybook/v021/#>

{%- for shape in shapes %}
{{shape.shapeID}} {
  {%- for statement in shape. statement_templates %}
  {{statement.property}} {{statement.propertyID}} 
  {%- if statement.valueNodeType %} {{statement.valueNodeType|upper}}{% endif -%}
  {%- if statement.valueDataType %} {{statement.valueDataType}}{% endif -%}
  {%- if statement.min or statement.max %} { {{-statement.min-}}
		{%- if statement.max -%}
		 ,{{statement.max}} 
		{%- endif -%} }
  {%- endif -%}
  {%- if statement.MaxInclusive %} MaxInclusive {{statement.MaxInclusive}} {%- endif -%}
  {%- if statement.MinInclusive %} MinInclusive {{statement.MinInclusive}} {%- endif -%}
  {%- if not loop.last -%} ;{%- endif -%}
  {%- endfor %}
}
{%- endfor %}
"""

st.subheader('3. ShEx Template in Jinja2')

shex_jinja = st.text_area('Edit the default ShEx Jinja2 Template', shex_jinja_default, height=len(shex_jinja_default.splitlines()) * PIXELS_PER_LINE,)

jinja_preview = st.expander("Click to preview current Jinja2 Template", expanded=False)
with jinja_preview:
	st.subheader('4. Current Jinja2 Template')
	st.code(shex_jinja, language='jinja2')

from jinja2 import Template
template = Template(shex_jinja)
shexc_output = template.render(ap_dict)

st.subheader('5. Generated ShExC')
st.code(shexc_output, language='trig')

st.subheader('6. Generated ShExJ')

json_ap=parse(shexc_output)._as_json
parsed = json.loads(json_ap)
st.code(json.dumps(parsed, indent=4, sort_keys=False), language='json')
