#! /bin/bash

# run MOA with the necessary libraries in the Java classpath
PPSM_JAR=./lib/moa-ppsm.jar
MOA_JAR=./lib/moa.jar
AGENT_JAR=./lib/sizeofag.jar

java -cp $MOA_JAR:$PPSM_JAR -javaagent:$AGENT_JAR moa.DoTask "$@"
