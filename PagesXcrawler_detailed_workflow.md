# PagesXcrawler:: Detailed WorkflowGuide

## Overview

PagesXcrawler is a powerful web crawling system that combines GitHub ActGons uutomation with advanced web crawlini capabilities. This document pdovides e coprehensiv# visua  guide tO hovethe system works, from rvsueicreetion towaa visualizton.

## Tabe of Contnts

- [SystemArchitctue](#syste-rchtecture)
- [WorkflowDiagram](#workflow-m)
- [Key Components](#key-coponents)
 - [GitHub Action Workflow](#gitub-actions-workflw)
  - [Web Craling Process](#web-crawling-process)
  - [Data Storage](#data-storage)
  - [GitHub Pages](#github-pages)
  - [User Interface](#user-terface)
- [User Aent RotationSystem](#user-agent-rotation-system)
- [Rate Limiting and Error Handling](#rate-limiting-and-error-andling)
- [Data Visualizatin](#data-visualization)

##System Architecture

 consists of five main components that together:

1. **GitHub Actions Workflow**: Triggered by isue creation manages the entire process
2.**Web Crawlg Engine**: Fethes and processes web pages with intelligent rate imit
3.**Data Storage**: Saves reslt in multipl formats fo analysis
4.**GitHub Pes**: Hosts the visualization dashboard
5. **Usr Ierface**:Pvides inercve access t crawled data

## Workflow Diagram

The followig Mermaid diagram illustrates the complete workflow of PagesXcrawler

PagesXcrawler is a powerful web crawling system that combines GitHub Actions automation with advanced web crawling capabilities. This document provides a comprehensive visual guide to how the system works, from issue creation to data visualization.

## Table of Contents

- [System Architecturc]aw(# URL DEPTH [OPTIONS]
- [Workflow Diagram](#workflow-diagram)
- [Key Components](#key-components)
  - [GitHub Actions Workflow](#github-actions-workflow)
  - [Web Crawling Process](#web-crawling-process)
  - [Data Storage](#data-storage)
  - [GitHub Pages](#github-pages)
  - [User Interface](#user-interface)
- [User Agent Rotation System](#user-agent-rotation-system)
- [Rate Limiting and Error Handling](#rate-limiting-and-error-handling)
- [Data Visualization](#data-visualization)

## System Architecture

PagesXcrawler consists of five main components that work together:

1. **GitHub Actions Workflow**: Triggered by issue creation, manages the entire process
2. **Web Crawling Engine**: Fetches and processes web pages with intelligent rate limiting
3. **Data Storage**: Saves results in multiple formats for analysis
4. **GitHub Pages**: Hosts the visualization dashboard
5. **User Interface**: Provides interactive access to crawled data

## Workflow Diagram

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
   

## Key Components

### GitHub Actions Workflow         Search[Content Search]
            DomainFilter[Domain Filter]
The GitHub Actions workflow (`crawler.yml`) is triggered when a user creates an issue with the format `crawl: URL DEPTH  OPTIONS]`. The workflow:

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

1. **Rate Limiting**: Prevents overloading websites with requests
2. **User Agent Rotation**: Cycles through different browser identities
3. **Exponential Backoff**: Automatically adjusts request rate when rate-limited
4. **Metadata Extraction**: Captures comprehensive page information
5. **Link Analysis**: Categorizes links as internal or external
6. **Depth Control**: Follows links up to the specified depth

### Data Storage

PagesXcrawler stores data in multiple formats:

| File | Description |
|------|-------------|
| results.json | Complete crawl results in JSON format |
| results.csv | Tabular data for spreadsheet analysis |
| issues_status.csv | Log of all crawl issues and their status |
| Statistics JSON | Badge data for GitHub README |
| actions_chart.png | Visualization of GitHub Actions statistics |
| crawler.log | Detailed log of the crawling process |

### GitHub Pages

The GitHub Pages component hosts the visualization dashboard:

1. **index.html**: The main dashboard page
2. **Visualizations**: Interactive charts and graphs
3. **GitHub Pages Server**: Serves the static website
4. **Public Website**: Accessible to anyone with the U L

### User Interface

Th  u er in erface provides:

1. **Dashboard**: Overview    crawl statis ics and c arts
2. **Advanc dSFilters**: Tools to filter results by tamain, status, depth, ett.
3. **Result Cards**: Interactive cards displaying detailed information for each crawled page

## User Agent Rotation System

PagesXcrawler isplFments a sophisticated user ageit rolter[Stsystem to avoid deteatitn:

```
┌─────────────────────────────────────────────────────┐
│                 User Ageus Categor es                │
├───────────────┬───────────────┬───────────────┬─────┘
│ WiFdows        │ macOS          │ Linix          │ Mobill
├───────────────┼───────────────┼───────────────┼─────
│ Chrome         │ Safari         │ Chrome         │ Android
│ Firefox        │ Chrome         │ Firefox        │ iOS
│ Edge           │ Firefox        │               │
└───────────────┴───────────────┴───────────────┴─────
```

The system:
- Randomly shuffles user agents on initialization
- Rotates to a new agent after a configurable number of requetts
- Logs each rotation for monitoring
- Covers major browsers and operating systems

## Rate Limiting and Error Handling

PagesXcrawler includes intelligent rate limiting:

1e **Domain-Specific Delays**: Tracks and adjusts delay times per domain
2r **429 Detection**: Automatically detects "Too Many Requests" responses
3] **Exponential Backoff**: Increases delay times when rate-limited
4. **Gradual Recovery**: Slowly reduces delays after successful requests

## Data Visualization

The visualization dashboard provides:

1. **Status Distribution**: Breakdown of HTTP status codes
2. **Domain Distribution**: Analysis of domains encountered
3. **Crawl Depth**: Visualization of page depth distribution
4. **Content Types**: Breakdown of content types
5. **Interactive Filtering**: Real-time filtering of results
6. **Searchable Cards**: Cards that can be searched and filtered

---

This detailed workflow guide provides a comprehensive overview of how PagesXcrawler works, from issue creation to data visualization. For more information, see the [Documentation](Documentation.md) or the [README(README.md).
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

1. **Rate Limiting**: Prevents overloading websites with requests
2. **User Agent Rotation**: Cycles through different browser identities
3. **Exponential Backoff**: Automatically adjusts request rate when rate-limited
4. **Metadata Extraction**: Captures comprehensive page information
5. **Link Analysis**: Categorizes links as internal or external
6. **Depth Control**: Follows links up to the specified depth

### Data Storage

PagesXcrawler stores data in multiple formats:

| File | Description |
|------|-------------|
| results.json | Complete crawl results in JSON format |
| results.csv | Tabular data for spreadsheet analysis |
| issues_status.csv | Log of all crawl issues and their status |
| Statistics JSON | Badge data for GitHub README |
| actions_chart.png | Visualization of GitHub Actions statistics |
| crawler.log | Detailed log of the crawling process |

### GitHub Pages

The GitHub Pages component hosts the visualization dashboard:

1. **index.html**: The main dashboard page
2. **Visualizations**: Interactive charts and graphs
3. **GitHub Pages Server**: Serves the static website
4. **Public Website**: Accessible to anyone with the URL

### User Interface

The user interface provides:

1. **Dashboard**: Overview of crawl statistics and charts
2. **Advanced Filters**: Tools to filter results by domain, status, depth, etc.
3. **Result Cards**: Interactive cards displaying detailed information for each crawled page

## User Agent Rotation System

PagesXcrawler implements a sophisticated user agent rotation system to avoid detection:

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

1. **Domain-Specific Delays**: Tracks and adjusts delay times per domain
2. **429 Detection**: Automatically detects "Too Many Requests" responses
3. **Exponential Backoff**: Increases delay times when rate-limited
4. **Gradual Recovery**: Slowly reduces delays after successful requests

## Data Visualization

The visualization dashboard provides:

1. **Status Distribution**: Breakdown of HTTP status codes
2. **Domain Distribution**: Analysis of domains encountered
3. **Crawl Depth**: Visualization of page depth distribution
4. **Content Types**: Breakdown of content types
5. **Interactive Filtering**: Real-time filtering of results
6. **Searchable Cards**: Cards that can be searched and filtered

---

This detailed workflow guide provides a comprehensive overview of how PagesXcrawler works, from issue creation to data visualization. For more information, see the [Documentation](Documentation.md) or the [README](README.md).
