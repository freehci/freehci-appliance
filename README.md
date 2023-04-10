# freehci-appliance

To run the prosject: 
`git clone https://github.com/freehci/freehci-appliance.git`

Install uvicorn using `pip install uvicorn`

Edit html/ui/static/js/config.js to point to your API endpoint.

window.apiBaseUrl = "http://localhost:8000/";

`uvicorn main:app --reload`