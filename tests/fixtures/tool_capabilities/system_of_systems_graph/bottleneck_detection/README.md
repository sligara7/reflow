# Tool Capability Test: Bottleneck Detection

## Tool

`system_of_systems_graph_v2.py` - Centrality analysis feature

## Purpose

Validate that the tool correctly identifies **bottlenecks** - services with high in-degree (many services depend on them).

## Scenario

**System**: Microservices architecture with 6 services:
- `api_gateway` - Central gateway that all backend services use
- `service_1` through `service_5` - Backend services that depend on api_gateway

**Architecture**:
```
service_1 ──┐
service_2 ──┤
service_3 ──┼─→ api_gateway
service_4 ──┤
service_5 ──┘
```

**Bottleneck**: `api_gateway` has in-degree of 5 (83% centrality in 6-node network)

## Expected Detection

**Command**:
```bash
python3 tools/system_of_systems_graph_v2.py \
  specs/machine/service_arch_index.json \
  --centrality \
  --output detected_output.json
```

**Expected Output**:
```json
{
  "graph_analysis": {
    "centrality": {
      "degree_centrality": {
        "api_gateway": 0.8333,  // 5/6 = 83.3%
        "service_1": 0.1667,
        "service_2": 0.1667,
        ...
      },
      "in_degree": {
        "api_gateway": 5,  // 5 services depend on it
        "service_1": 0,
        ...
      }
    }
  }
}
```

## Why This Is Important

**Bottleneck Risks**:
1. **Single Point of Failure** - If api_gateway fails, all 5 services fail
2. **Performance Bottleneck** - All traffic flows through gateway (latency, throughput limits)
3. **Scalability Limit** - Gateway must handle aggregate load of all services
4. **Deployment Risk** - Gateway updates affect all services

**Mitigation Strategies**:
1. **Redundancy**: Deploy multiple gateway instances (load balancer)
2. **Caching**: Reduce gateway load with caching layer
3. **Service Mesh**: Distribute routing logic (Istio, Linkerd)
4. **Decomposition**: Break gateway into smaller, specialized gateways

## Pass Criteria

- Degree centrality of `api_gateway` >= 0.7 (high centrality)
- In-degree of `api_gateway` >= 5 (5 dependents)
- Tool generates centrality analysis successfully
- No errors or crashes

## Test Category

**Tool Capabilities** → **system_of_systems_graph** → **bottleneck_detection**

## Related Tests

- `knowledge_gaps/01_orphaned_interface` - Opposite problem (unused service)
- `centrality_analysis/` - Validates all centrality metrics
- `orphaned_nodes/` - Services with 0 in-degree AND 0 out-degree
