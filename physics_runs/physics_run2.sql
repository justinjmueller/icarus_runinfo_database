SELECT run_number
FROM runinfo
WHERE     run_number>=9301
      AND run_number<=10097
      AND cathodehv>74000
      AND tpc_components=96 
      AND pmt_components=24
      AND crt_components>=24
      AND instr(configuration, "Physics_General_thr390_Majority_5_9_OverlappingWindow");