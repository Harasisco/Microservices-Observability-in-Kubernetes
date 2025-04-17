# Technical Take-Home Assignment
## Microservices Observability in Kubernetes

### Overview
Create a simple two-service application deployed on Kubernetes with basic monitoring and tracing. The application will calculate a SHA256 hash and length of a given input string. The focus is on implementing proper observability practices in a Kubernetes environment.

### Requirements

#### Application Components
1. Hash Service
   - Single endpoint: POST /hash
   - Input: Plain text string
   - Output: SHA256 hash of the input
   - Technology: Any backend language/framework of choice

2. Length Service
   - Single endpoint: POST /length
   - Input: Plain text string
   - Output: Length of the string
   - Technology: Any backend language/framework of choice

Note: No frontend is required. Services can be tested using curl or Postman.

#### Infrastructure Requirements
- Deploy services on Kubernetes (minikube or kind is acceptable)
- Create appropriate Services and Deployments
- Configure simple health checks
- Use ConfigMaps for service configuration

#### Observability Requirements
- Deploy Jaeger using Helm chart
- Deploy Prometheus using Helm chart
- Implement request tracing using OpenTelemetry
- Collect basic metrics:
  - Request duration
  - Request count
  - Error count

### Example Request Flow
bash
# Example curl to hash service
curl -X POST http://localhost:8080/hash -d "Apple"
# Returns: f223faa96f22916294922b171a2696d868fd1f9129302eb41a45b2a2ea2ebbfd

# Example curl to length service
curl -X POST http://localhost:8081/length -d "Apple"
# Returns: 5

### Deliverables
1. Source code and Dockerfiles for both services
2. Kubernetes manifests for:
   - Deployments
   - Services
   - ConfigMaps
3. Brief README with:
   - Setup instructions
   - Example requests
   - How to view traces and metrics

### Evaluation Criteria
1. Working services with proper error handling
2. Correct Kubernetes configuration
3. Successful implementation of tracing between services
4. Basic metrics collection
5. Clear documentation

### Submission
- Provide a Git repository with your solution
- Include screenshots of:
  - A sample trace in Jaeger
  - Basic metrics in Prometheus
  - kubectl get all output showing your running services

### Additional Contributions
We welcome and encourage any additional improvements or suggestions beyond the basic requirements. This could include enhanced security measures, automated testing, CI/CD pipelines, custom dashboards, or any other features you believe would add value to the solution. Feel free to document your ideas even if you don't have time to implement them all.