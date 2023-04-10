# freehci-appliance

## Prerequisites

- Python 3.8 or later (may work with other versions as well)
- pip (Python package manager)

## Getting Started

1. Clone the repository:
`git clone https://github.com/freehci/freehci-appliance.git`

2. Install `uvicorn` using `pip`:
`pip install uvicorn`

3. Configure the Vue.js frontend to work with the FreeHCI API.

4. Edit `html/ui/static/js/config.js` to point to your API endpoint:

```javascript
window.apiBaseUrl = "http://localhost:8000/";
```

5. Run the project using `uvicorn`:
`uvicorn main:app --reload`

Options:
  --host TEXT                     Bind socket to this host.  [default: 127.0.0.1]
  --port INTEGER                  Bind socket to this port.  [default: 8000]

For more options, please visit [https://www.uvicorn.org/](uvicorn documentation)