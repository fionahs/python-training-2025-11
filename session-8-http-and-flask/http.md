## HTTP Essentials


### What is HTTP?

- Protocol for client-server communication
- Request → Server processes → Response

Slides: https://docs.google.com/presentation/d/e/2PACX-1vSxS5iMjTveO-IBqdDE65dgouZStLTW-Vlyt3N9js3FnMCeW8cwSgmrkGzX2i_g0qGCM6fJDKZ-r3Se/pub?start=false&loop=false&delayms=3000&slide=id.g7fabbaef24_1_232

### HTTP Methods (CRUD Operations)
- GET    - Read/Retrieve data
- POST   - Create new data
- PUT    - Update existing data
- DELETE - Remove data

### Status Codes
- 2xx - Success
  200 OK        - Request succeeded
  201 Created   - Resource created

- 4xx - Client Errors
  400 Bad Request - Invalid data
  404 Not Found   - Resource doesn't exist

- 5xx - Server Errors
  500 Internal Server Error

### HTTPS vs HTTP

HTTP: Plain text (insecure)
HTTPS: Encrypted with SSL/TLS

- Protects data in transit
- Prevents eavesdropping
- Verifies server identity