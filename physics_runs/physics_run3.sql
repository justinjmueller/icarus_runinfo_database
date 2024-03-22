SELECT run_number
FROM runinfo
WHERE     run_number>=11799
      AND cathodehv>74000
      AND tpc_components=96 
      AND pmt_components=24
      AND crt_components>=24
      AND instr(configuration, "Physics_Standard_Both_WithTPCCompression_Run3");