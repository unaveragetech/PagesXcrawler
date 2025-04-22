# PagesXcrawler: Detailed Workflow Guide

## Overview

PagesXcrawler is a powerful web crawling system that combines GitHub Actions automation with advanced web crawling capabilities. This document provides a comprehensive visual guide to how the system works, from issue creation to data visualization.

## Table of Contents

- [System Architecture](#system-architecture)
- [Workflow Diagrams](#workflow-diagrams)
  - [Complete System Overview](#complete-system-overview)
  - [GitHub Actions Workflow](#github-actions-workflow-diagram)
  - [Web Crawling Process](#web-crawling-process-diagram)
  - [Data Flow Diagram](#data-flow-diagram)
  - [User Interface Components](#user-interface-components)
- [Key Components](#key-components)
- [User Agent Rotation System](#user-agent-rotation-system)
- [Rate Limiting and Error Handling](#rate-limiting-and-error-handling)
- [Data Visualization](#data-visualization)

## System Architecture

PagesXcrawler consists of five main components that work together:

```mermaid
graph TD
    subgraph "PagesXcrawler System Architecture"
        A[GitHub Actions Workflow] --> B[Web Crawling Engine]
        B --> C[Data Storage]
        C --> D[GitHub Pages]
        D --> E[User Interface]
        
        A -->|Triggers| B
        B -->|Saves to| C
        C -->|Provides data for| D
        D -->|Renders| E
    end
    
    classDef primary fill:#f9d5e5,stroke:#333,stroke-width:2px;
    classDef secondary fill:#d5f5e3,stroke:#333,stroke-width:1px;
    
    class A,B primary;
    class C,D,E secondary;
```

1. **GitHub Actions Workflow**: Triggered by issue creation, manages the entire process
2. **Web Crawling Engine**: Fetches and processes web pages with intelligent rate limiting
3. **Data Storage**: Saves results in multiple formats for analysis
4. **GitHub Pages**: Hosts the visualization dashboard
5. **User Interface**: Provides interactive access to crawled data

## Workflow Diagrams

### Complete System Overview

The following Mermaid diagram illustrates the complete workflow of PagesXcrawler:

```mermaid
flowchart TD
    %% Main components
    User([User]) --> CreateIssue[Create GitHub Issue]
    CreateIssue -->|"crawl: URL DEPTH [OPTIONS]"| GHActions[GitHub Actions]
    
    %% GitHub Actions Workflow
    subgraph GHWorkflow["GitHub Actions Workflow (crawler.yml)"]
        direction TB
        Checkout[Checkout Repository] --> SetupPython[Setup Python]
        SetupPython --> InstallDeps[Install Dependencies]
        InstallDeps --> ExtractParams[Extract URL & Parameters]
        ExtractParams --> AddComment1[Add Initial Comment]
        AddComment1 --> RunCrawler[Run crawler.py]
        RunCrawler --> UpdateProgress[Update Progress Comment]
        UpdateProgress --> SaveResults[Save Results]
        SaveResults --> UpdateHTML[Run update_html.py]
        UpdateHTML --> LogStatus[Log Issue Status]
        LogStatus --> AddComment2[Add Final Comment]
        AddComment2 --> Delay[30s Delay]
        Delay --> CloseIssue[Close Issue]
        CloseIssue --> CountStats[Count Stats]
        CountStats --> GenCharts[Generate Charts]
        GenCharts --> CommitPush[Commit & Push]
    end
    
    GHActions --> GHWorkflow
    
    %% Crawler Process
    subgraph CrawlerProcess["Web Crawling Process (crawler.py)"]
        direction TB
        StartCrawl[Start at URL] --> InitRate[Initialize Rate Limiter]
        InitRate --> InitAgents[Initialize User Agents]
        InitAgents --> CheckRotation[Check Rotation Counter]
        CheckRotation --> |"Need Rotation"| RotateAgent[Rotate User Agent]
        CheckRotation --> |"No Rotation Needed"| FetchHTML[Fetch HTML]
        RotateAgent --> FetchHTML
        FetchHTML --> CheckRate[Check Rate Limits]
        CheckRate -->|429 Error| BackOff[Exponential Backoff]
        BackOff --> CheckRotation
        CheckRate -->|Success| ParseHTML[Parse with BeautifulSoup]
        ParseHTML --> ExtractMeta[Extract Metadata]
        ParseHTML --> ExtractLinks[Extract Links]
        ExtractLinks --> FilterLinks[Filter Links]
        FilterLinks --> |Internal Links| FollowLinks[Follow Links]
        FollowLinks --> |Depth < Max| CheckRotation
        ExtractMeta --> CollectData[Collect Data]
        
        subgraph UserAgents["User Agent Categories"]
            direction TB
            Windows[Windows Browsers]
            MacOS[macOS Browsers]
            Linux[Linux Browsers]
            Mobile[Mobile Browsers]
        end
        
        InitAgents --> UserAgents
    end
    
    RunCrawler --> CrawlerProcess
    CollectData --> SaveResults
    
    %% Data Storage
    subgraph DataStorage["Data Storage"]
        direction TB
        ResultsJSON[results.json]
        ResultsCSV[results.csv]
        IssuesStatus[issues_status.csv]
        StatsJSON[Statistics JSON Files]
        ChartPNG[actions_chart.png]
        ErrorLog[crawler.log]
    end
    
    SaveResults --> ResultsJSON
    SaveResults --> ResultsCSV
    LogStatus --> IssuesStatus
    GenCharts --> StatsJSON
    GenCharts --> ChartPNG
    CrawlerProcess --> ErrorLog
    
    %% GitHub Pages
    subgraph GHPages["GitHub Pages"]
        direction TB
        IndexHTML[index.html]
        subgraph Visualizations["Data Visualizations"]
            StatusChart[Status Distribution]
            DomainChart[Domain Distribution]
            DepthChart[Crawl Depth]
            ContentChart[Content Types]
        end
        GHPagesServer[GitHub Pages Server]
        PublicSite[Public Website]
    end
    
    UpdateHTML --> IndexHTML
    UpdateHTML --> Visualizations
    CommitPush --> GHPagesServer
    GHPagesServer --> PublicSite
    
    %% User Interface
    subgraph UserInterface["User Interface"]
        direction TB
        subgraph Dashboard["Dashboard"]
            Overview[Statistics Overview]
            Charts[Interactive Charts]
        end
        subgraph Filters["Advanced Filters"]
            Search[Content Search]
            DomainFilter[Domain Filter]
            StatusFilter[Status Filter]
            DepthFilter[Depth Filter]
        end
        subgraph Results["Result Cards"]
            StatusBadge[Status Indicators]
            MetaInfo[Metadata Display]
            SizeStats[Size & Performance]
            LinkAnalysis[Link Analysis]
            SEOMetrics[SEO Metrics]
        end
    end
    
    PublicSite --> UserInterface
    
    %% Styling
    classDef user fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef github fill:#eeeeee,stroke:#333,stroke-width:1px;
    classDef crawler fill:#d5f5e3,stroke:#333,stroke-width:1px;
    classDef data fill:#d6eaf8,stroke:#333,stroke-width:1px;
    classDef pages fill:#fdebd0,stroke:#333,stroke-width:1px;
    classDef ui fill:#e8daef,stroke:#333,stroke-width:1px;
    
    class User,CreateIssue user;
    class GHActions,GHWorkflow github;
    class CrawlerProcess crawler;
    class DataStorage data;
    class GHPages pages;
    class UserInterface ui;
```

### GitHub Actions Workflow Diagram

This diagram focuses specifically on the GitHub Actions workflow:

```mermaid
sequenceDiagram
    participant User
    participant GitHub as GitHub Issues
    participant Actions as GitHub Actions
    participant Crawler as Crawler.py
    participant Storage as Data Storage
    participant Pages as GitHub Pages
    
    User->>GitHub: Create Issue with format:<br>crawl: URL DEPTH [OPTIONS]
    GitHub->>Actions: Trigger workflow
    
    Note over Actions: crawler.yml workflow starts
    
    Actions->>Actions: Checkout repository
    Actions->>Actions: Setup Python environment
    Actions->>Actions: Install dependencies
    
    Actions->>GitHub: Add initial comment
    
    Actions->>Crawler: Run crawler with parameters
    
    loop Until complete
        Crawler->>GitHub: Update progress comments
        Crawler->>Storage: Save partial results
    end
    
    Crawler->>Storage: Save final results
    
    Actions->>Pages: Update visualization
    Actions->>Storage: Log issue status
    
    Actions->>GitHub: Add completion comment
    Actions->>GitHub: Close issue
    
    Actions->>Actions: Generate statistics
    Actions->>GitHub: Commit and push changes
    
    Pages->>User: Display results dashboard
```

### Web Crawling Process Diagram

This diagram details the web crawling process and rate limiting:

```mermaid
stateDiagram-v2
    [*] --> Initialize
    
    state Initialize {
        [*] --> SetupRateLimiter
        SetupRateLimiter --> InitializeUserAgents
        InitializeUserAgents --> [*]
    }
    
    Initialize --> CheckRotation
    
    state CheckRotation {
        [*] --> NeedRotation
        [*] --> NoRotationNeeded
        NeedRotation --> RotateAgent
        NoRotationNeeded --> [*]
        RotateAgent --> [*]
    }
    
    CheckRotation --> FetchPage
    
    state FetchPage {
        [*] --> SendRequest
        SendRequest --> CheckResponse
        
        state CheckResponse {
            [*] --> Success
            [*] --> RateLimited
            [*] --> Error
            
            RateLimited --> IncreaseDelay
            IncreaseDelay --> [*]
            
            Success --> DecreaseDelay
            DecreaseDelay --> [*]
            
            Error --> LogError
            LogError --> [*]
        }
    }
    
    FetchPage --> ProcessPage: Success
    FetchPage --> CheckRotation: Rate Limited
    
    state ProcessPage {
        [*] --> ParseHTML
        ParseHTML --> ExtractMetadata
        ParseHTML --> FindLinks
        
        state FindLinks {
            [*] --> FilterLinks
            FilterLinks --> CategorizeLinks
            
            state CategorizeLinks {
                [*] --> Internal
                [*] --> External
            }
        }
        
        ExtractMetadata --> CollectData
        FindLinks --> CollectData
    }
    
    ProcessPage --> SaveResults: Max Depth Reached
    ProcessPage --> CheckRotation: Follow Internal Links
    
    SaveResults --> [*]
```

### Data Flow Diagram

This diagram shows how data flows through the system:

```mermaid
graph LR
    subgraph Input
        A[GitHub Issue] -->|URL & Parameters| B[GitHub Actions]
    end
    
    subgraph Processing
        B -->|Triggers| C[Crawler Engine]
        C -->|Fetches| D[Web Pages]
        D -->|Returns| C
        C -->|Processes| E[Raw Data]
    end
    
    subgraph Storage
        E -->|Saved as| F[JSON]
        E -->|Saved as| G[CSV]
        E -->|Logs| H[Status CSV]
        E -->|Generates| I[Statistics]
    end
    
    subgraph Visualization
        F -->|Powers| J[Dashboard]
        G -->|Available for| K[Download]
        H -->|Tracks| L[History]
        I -->|Creates| M[Charts]
    end
    
    classDef input fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef process fill:#d5f5e3,stroke:#333,stroke-width:1px;
    classDef storage fill:#d6eaf8,stroke:#333,stroke-width:1px;
    classDef visual fill:#fdebd0,stroke:#333,stroke-width:1px;
    
    class A,B input;
    class C,D,E process;
    class F,G,H,I storage;
    class J,K,L,M visual;
```

### User Interface Components

This diagram illustrates the components of the user interface:

```mermaid
graph TD
    subgraph Dashboard
        A[Main Dashboard] --> B[Statistics Overview]
        A --> C[Interactive Charts]
        A --> D[Filter Controls]
        A --> E[Result Cards Container]
    end
    
    subgraph Filters
        D --> F[Search Box]
        D --> G[Domain Dropdown]
        D --> H[Status Filter]
        D --> I[Depth Slider]
        D --> J[Content Type Filter]
    end
    
    subgraph ResultCards
        E --> K[Card 1]
        E --> L[Card 2]
        E --> M[Card 3]
        E --> N[More Cards...]
        
        subgraph CardComponents
            K --> O[Status Badge]
            K --> P[URL Display]
            K --> Q[Metadata Section]
            K --> R[Link Analysis]
            K --> S[Performance Metrics]
        end
    end
    
    classDef dashboard fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef filters fill:#d5f5e3,stroke:#333,stroke-width:1px;
    classDef cards fill:#d6eaf8,stroke:#333,stroke-width:1px;
    classDef components fill:#fdebd0,stroke:#333,stroke-width:1px;
    
    class A,B,C,D,E dashboard;
    class F,G,H,I,J filters;
    class K,L,M,N cards;
    class O,P,Q,R,S components;
```

## Key Components

### GitHub Actions Workflow

The GitHub Actions workflow (`crawler.yml`) is triggered when a user creates an issue with the format `crawl: URL DEPTH [OPTIONS]`. The workflow:

1. **Checkout Repository**: Clones the repository to the GitHub Actions runner
2. **Setup Python**: Installs Python 3.8 on the runner
3. **Install Dependencies**: Installs required packages (requests, BeautifulSoup4)
4. **Extract Parameters**: Parses the issue title to extract URL, depth, and options
5. **Add Initial Comment**: Posts a comment with the configuration details
6. **Run Crawler**: Executes the crawler.py script with the extracted parameters
7. **Update Progress**: Posts progress updates as comments on the issue
8. **Save Results**: Stores the crawl results in JSON and CSV formats
9. **Update HTML**: Generates the visualization dashboard
10. **Log Status**: Records the issue status in issues_status.csv
11. **Add Final Comment**: Posts a completion comment with links to results
12. **Close Issue**: Automatically closes the issue when crawling is complete
13. **Generate Statistics**: Counts deployments and actions, generates charts
14. **Commit & Push**: Pushes all changes back to the repository

### Web Crawling Process

The crawler.py script implements an intelligent web crawler with:

```mermaid
graph TD
    A[Start Crawl] --> B[Initialize Rate Limiter]
    B --> C[Initialize User Agents]
    C --> D{Need to Rotate<br>User Agent?}
    D -->|Yes| E[Rotate User Agent]
    D -->|No| F[Fetch HTML]
    E --> F
    F --> G{Rate Limited?}
    G -->|Yes| H[Apply Backoff]
    H --> D
    G -->|No| I[Parse HTML]
    I --> J[Extract Metadata]
    I --> K[Extract Links]
    K --> L[Filter Links]
    L --> M{More Links<br>to Follow?}
    M -->|Yes| N{Depth < Max?}
    N -->|Yes| D
    N -->|No| O[Collect Data]
    M -->|No| O
    J --> O
    O --> P[Save Results]
```

Key features:
1. **Rate Limiting**: Prevents overloading websites with requests
2. **User Agent Rotation**: Cycles through different browser identities
3. **Exponential Backoff**: Automatically adjusts request rate when rate-limited
4. **Metadata Extraction**: Captures comprehensive page information
5. **Link Analysis**: Categorizes links as internal or external
6. **Depth Control**: Follows links up to the specified depth

### Data Storage

PagesXcrawler stores data in multiple formats:

```mermaid
classDiagram
    class DataStorage {
        +results.json
        +results.csv
        +issues_status.csv
        +statistics_json_files
        +actions_chart.png
        +crawler.log
    }
    
    class ResultsJSON {
        +url: string
        +title: string
        +meta_description: string
        +internal_links: array
        +external_links: array
        +status_code: number
        +content_size: number
        +crawl_timestamp: datetime
    }
    
    class ResultsCSV {
        +url: string
        +title: string
        +status_code: number
        +internal_link_count: number
        +external_link_count: number
        +content_size: number
    }
    
    class IssuesStatus {
        +issue_number: number
        +issue_title: string
        +status: string
        +timestamp: datetime
    }
    
    DataStorage <|-- ResultsJSON
    DataStorage <|-- ResultsCSV
    DataStorage <|-- IssuesStatus
```

| File | Description |
|------|-------------|
| results.json | Complete crawl results in JSON format |
| results.csv | Tabular data for spreadsheet analysis |
| issues_status.csv | Log of all crawl issues and their status |
| Statistics JSON | Badge data for GitHub README |
| actions_chart.png | Visualization of GitHub Actions statistics |
| crawler.log | Detailed log of the crawling process |

## User Agent Rotation System

PagesXcrawler implements a sophisticated user agent rotation system to avoid detection:

```mermaid
pie title User Agent Distribution
    "Windows Browsers" : 8
    "macOS Browsers" : 6
    "Linux Browsers" : 4
    "Mobile Browsers" : 4
```

```
┌─────────────────────────────────────────────────────┐
│                 User Agent Categories                │
├───────────────┬───────────────┬───────────────┬─────┘
│ Windows        │ macOS          │ Linux          │ Mobile
├───────────────┼───────────────┼───────────────┼─────
│ Chrome         │ Safari         │ Chrome         │ Android
│ Firefox        │ Chrome         │ Firefox        │ iOS
│ Edge           │ Firefox        │               │
└───────────────┴───────────────┴───────────────┴─────
```

The system:
- Randomly shuffles user agents on initialization
- Rotates to a new agent after a configurable number of requests
- Logs each rotation for monitoring
- Covers major browsers and operating systems

## Rate Limiting and Error Handling

PagesXcrawler includes intelligent rate limiting:

```mermaid
graph TD
    A[Request] --> B{Rate Limited?}
    B -->|Yes: 429 Response| C[Increase Delay]
    B -->|No: 200 Response| D[Decrease Delay]
    
    C --> E[Exponential Backoff]
    E --> F[Log Warning]
    F --> G[Wait]
    G --> A
    
    D --> H[Gradual Recovery]
    H --> A
    
    subgraph "Domain-Specific Delay Tracking"
        I[example.com: 0.5s]
        J[github.com: 2.0s]
        K[wikipedia.org: 1.0s]
    end
```

1. **Domain-Specific Delays**: Tracks and adjusts delay times per domain
2. **429 Detection**: Automatically detects "Too Many Requests" responses
3. **Exponential Backoff**: Increases delay times when rate-limited
4. **Gradual Recovery**: Slowly reduces delays after successful requests

## Data Visualization

The visualization dashboard provides:

```mermaid
graph LR
    subgraph "Dashboard Components"
        A[Status Distribution] --> B[Pie Chart]
        C[Domain Distribution] --> D[Bar Chart]
        E[Crawl Depth] --> F[Tree Map]
        G[Content Types] --> H[Donut Chart]
    end
    
    subgraph "Interactive Features"
        I[Search] --> J[Filter Cards]
        K[Domain Filter] --> J
        L[Status Filter] --> J
        M[Depth Filter] --> J
    end
    
    subgraph "Result Cards"
        J --> N[Filtered Results]
        N --> O[Card 1]
        N --> P[Card 2]
        N --> Q[Card 3]
    end
```

1. **Status Distribution**: Breakdown of HTTP status codes
2. **Domain Distribution**: Analysis of domains encountered
3. **Crawl Depth**: Visualization of page depth distribution
4. **Content Types**: Breakdown of content types
5. **Interactive Filtering**: Real-time filtering of results
6. **Searchable Cards**: Cards that can be searched and filtered

---

This detailed workflow guide provides a comprehensive overview of how PagesXcrawler works, from issue creation to data visualization. For more information, see the [Documentation](Documentation.md) or the [README](README.md).
