#! /bin/bash

# useful colored output commands
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`
bold=`tput bold`

# script variables
modifiers=""
moaJar=./lib/moa.jar
ppsmJar=./lib/moa-ppsm.jar
agentJar=./lib/sizeofag.jar

function usage {
  echo "${bold}Usage: `basename $0` [-h|--help] [OPTIONS] MOA_COMMANDS${reset}"
  echo ""
  echo "  Utility to execute Tasks within the MOA package, with the privacy extension"
  echo "  library MOA-PPSM (check https://github.com/necavit/moa-ppsm). The utility"
  echo "  automatically calls Java and sets the classpath with the required libraries"
  echo "  (see the LIBRARIES section below) and executes the MOA commands that are"
  echo "  specified in MOA_COMMANDS. Some OPTIONS are available to suppress some of"
  echo "  the output of the MOA framework (useful to let other scripts parse the output)."
  echo ""
  echo " LIBRARIES"
  echo "    All of the following libraries (JARs) are required:"
  echo "    ${bold}lib/moa-ppsm.jar${reset}"
  echo "        Privacy filters extension library. You may change the default location"
  echo "        by using the environment variable: PPSM_JAR"
  echo "    ${bold}lib/moa.jar${reset}"
  echo "        The MOA release JAR. Be aware that the version against which MOA-PPSM"
  echo "        is compiled is 2013.11. You may change the default location by using"
  echo "        the environment variable: MOA_JAR"
  echo "    ${bold}lib/sizeofag.jar${reset}"
  echo "        A dependecy that MOA requires. You may change the default location by"
  echo "        using the environment varaible: AGENT_JAR"
  echo " OPTIONS"
  echo "    ${bold}-h|--help${reset}"
  echo "        Displays this usage page and exits"
  echo "    ${bold}-e|--silence-error${reset}"
  echo "        Silences the output that MOA writes on the ${bold}stderr${reset} stream."
  echo "        No information about the task or its progress will be shown."
  echo "    ${bold}-o|--silence-output${reset}"
  echo "        Silences the output that MOA writes on the ${bold}stdout${reset} stream."
  echo "        No information about the result of the task (report) will be shown."
  exit 1
}

function checkLib {
  if [[ ! -f "$1" ]]; then
    echo "${red}Error: the required library at $1 does not exist or is not a regular file.${reset}"
    exit 1
  fi
}

function executeMoa {
  java -cp $moaJar:$ppsmJar -javaagent:$agentJar moa.DoTask "$@" $modifiers
}

function parseOpts {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
  elif [[ "$1" == "-e" || "$1" == "--silence-error" ]]; then
    modifiers="$modifiers -S" # -S CLI option for moa.doTask (see MOA API)
    shift
    parseOpts "$@"
  elif [[ "$1" == "-o" || "$1" == "--silence-output" ]]; then
    modifiers="$modifiers -R" # -R CLI option for moa.doTask (see MOA API)
    shift
    parseOpts "$@"
  else
    executeMoa "$@"
  fi
}

# script main execution
  # check for externally set variables
if [[ ! -z $MOA_JAR ]]; then
  moaJar=$MOA_JAR
fi
if [[ ! -z $PPSM_JAR ]]; then
  ppsmJar=$PPSM_JAR
fi
if [[ ! -z $AGENT_JAR ]]; then
  agentJar=$AGENT_JAR
fi
  # check the location of the libraries
checkLib $moaJar
checkLib $ppsmJar
checkLib $agentJar
  # parse this script options
parseOpts $@
