```mermaid
graph TD
    subgraph 优化前查询树 (Unoptimized Tree)
    T1[π VideoID, Title, Username] --- J1[Join ⋈]
    J1 --- J2[Join ⋈]
    J1 --- C1[CATEGORY]
    J2 --- U1[USER]
    J2 --- S1[σ Status='Approved']
    S1 --- V1[VIDEO 全表扫描]
    end

    subgraph 优化后推导树 (Selection Push Down Tree)
    T2[π VideoID, Title, Username] --- J3[Join ⋈]
    J3 --- J4[Join ⋈]
    J3 --- C2[CATEGORY]
    J4 --- U2[USER]
    J4 --- Filter[σ Status='Approved' VIDEO 提前过滤]
    end
    
    style Filter fill:#ffe0b2,stroke:#f57c00
    style S1 fill:#fff9c4,stroke:#fbc02d
```