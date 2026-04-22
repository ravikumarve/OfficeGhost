#!/bin/bash
# GhostOffice CLI completion for Bash

_ghostoffice_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="
        --dry-run
        --test-email
        --test-files
        --continuous
        --status
        --help
        --version
    "
    
    # Main options
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
        return 0
    fi
    
    # Flags don't take arguments
    case $prev in
        --dry-run|--test-email|--test-files|--continuous|--status|--help|--version)
            return 0
            ;;
    esac
}

complete -F _ghostoffice_completions python3
complete -F _ghostoffice_completions python
complete -F _ghostoffice_completions main.py