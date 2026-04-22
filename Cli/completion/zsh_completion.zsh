# GhostOffice CLI completion for Zsh
# Save this to ~/.zsh/completions/_ghostoffice

_ghostoffice() {
    local -a opts
    opts=(
        '--dry-run[Run without making changes]'
        '--test-email[Test email processing]'
        '--test-files[Test file processing]'
        '--continuous[Run continuously]'
        '--status[Show status and exit]'
        '--help[Show help message]'
        '--version[Show version]'
    )
    
    _describe 'options' opts
}

compdef _ghostoffice python3
compdef _ghostoffice python
compdef _ghostoffice main.py