```mermaid
graph TD
    subgraph Root [B+Tree Index Root Node: Status, CategoryID]
        R["Root Page: Key Ranges [Approved | Draft | Pending]"]
    end

    subgraph Internal [Internal Nodes]
        I1["Page 2: Approved Category 1..10"]
        I2["Page 3: Draft / Pending Category 1..10"]
    end

    subgraph Leaves [Leaf Nodes: Linked List for Range Scan]
        L1["Leaf 1: Approved, Cat 1 (Video 101, 102)"] <--> L2["Leaf 2: Approved, Cat 2 (Video 105, 108)"]
        L2 <--> L3["Leaf 3: Approved, Cat 3 (Video 112, 115)"]
    end

    R --> I1
    R --> I2
    I1 --> L1
    I1 --> L2
    I1 --> L3

    style Root fill:#e8eaf6,stroke:#3f51b5
    style Internal fill:#e1f5fe,stroke:#0288d1
    style Leaves fill:#e8f5e9,stroke:#388e3c