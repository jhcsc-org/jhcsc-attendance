```
flowchart TD
    C[Pi Camera/USB Camera] <--> VS[Video Stream Service\nUV4L/MJPEG]
    VS <--> P[Python Backend\nFastAPI]
    
    subgraph Backend [Python Backend - Resource Optimized]
        P --> CV[OpenCV-lite]
        CV --> SL[(SQLite)]
        P --> S3[Supabase S3]
        SL <--> SYNC[Data Sync Service]
        SYNC <--> SDB[(Supabase DB)]
        P --> CACHE[In-Memory Cache\nRedis Lite]
    end
    
    subgraph Frontend [React Frontend - Progressive Web App]
        R[React App] --> SR[Student Registration]
        R --> AT[Attendance Tracking]
        R <--> AUTH[Supabase Auth]
        R --> PWA[Service Worker\nOffline Support]
    end
    
    P <--> R
    
    subgraph RPi [RPi Optimizations]
        OPT1[CPU Governor\nPerformance Mode]
        OPT2[Swap Space\n1GB]
        OPT3[OpenCV\nARM Optimized]
    end
```