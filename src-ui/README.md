# Document classification UI

## Installation
To install the web interface, it is possible to create a `.env` file containing these variables:

```
VUE_APP_TOKEN=
VUE_APP_API_URL=
VUE_PUBLIC_PATH=
```

where

* `VUE_APP_TOKEN` is the token needed to access the API (see `src-api` folder for more information)
* `VUE_APP_API_URL` is the base URL of the API
* `VUE_PUBLIC_PATH` is the path where the built project will be reachable
  (for example, if the final URL will be `https://www.example.com/ui/`,
  this variable needs to be set to `/ui/`)

Install dependencies, running
```
npm install
```

Then the project can be built using the command
```
npm run build
```

The resulting `dist` folder will contain the HTML/JS/CSS compiled files.