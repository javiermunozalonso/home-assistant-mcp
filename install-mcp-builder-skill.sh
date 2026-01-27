#!/usr/bin/env bash

################################################################################
# Script: install-mcp-builder-skill.sh
# Description: Automates installation and updates of the mcp-builder skill
#              from Anthropic's skills repository into local project
# Usage: ./install-mcp-builder-skill.sh [--update] [--install-deps]
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="anthropics/skills"
GITHUB_BRANCH="main"
SKILL_NAME="mcp-builder"
BASE_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/skills/${SKILL_NAME}"
LOCAL_SKILL_DIR=".claude/skills/${SKILL_NAME}"

# Parse command line arguments
UPDATE_MODE=false
INSTALL_DEPS=false

for arg in "$@"; do
    case $arg in
        --update)
            UPDATE_MODE=true
            shift
            ;;
        --install-deps)
            INSTALL_DEPS=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --update        Update existing skill files"
            echo "  --install-deps  Install Python dependencies for skill scripts"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Fresh installation"
            echo "  $0 --update           # Update existing skill"
            echo "  $0 --install-deps     # Install with Python dependencies"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_step() {
    echo -e "${BLUE}→ $1${NC}"
}

# Check dependencies
check_dependencies() {
    print_header "Checking Dependencies"

    local missing_deps=()

    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi

    if ! command -v git &> /dev/null; then
        print_info "git not found (optional, but recommended)"
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install them and try again."
        exit 1
    fi

    print_success "All required dependencies found"
}

# Create directory structure
create_directories() {
    print_header "Creating Directory Structure"

    mkdir -p "${LOCAL_SKILL_DIR}/reference"
    mkdir -p "${LOCAL_SKILL_DIR}/scripts"

    print_success "Directories created: ${LOCAL_SKILL_DIR}"
}

# Download a file from GitHub
download_file() {
    local file_path="$1"
    local local_path="${LOCAL_SKILL_DIR}/${file_path}"
    local url="${BASE_URL}/${file_path}"

    print_step "Downloading: ${file_path}"

    if curl -f -sS -o "${local_path}" "${url}"; then
        print_success "Downloaded: ${file_path}"
        return 0
    else
        print_error "Failed to download: ${file_path}"
        return 1
    fi
}

# Download all skill files
download_skill_files() {
    print_header "Downloading Skill Files"

    local files=(
        "SKILL.md"
        "LICENSE.txt"
        "reference/evaluation.md"
        "reference/mcp_best_practices.md"
        "reference/python_mcp_server.md"
        "reference/node_mcp_server.md"
        "scripts/connections.py"
        "scripts/evaluation.py"
        "scripts/example_evaluation.xml"
        "scripts/requirements.txt"
    )

    local success_count=0
    local total_count=${#files[@]}

    for file in "${files[@]}"; do
        if download_file "$file"; then
            ((success_count++))
        fi
    done

    echo ""
    print_info "Downloaded ${success_count}/${total_count} files"

    if [ $success_count -eq $total_count ]; then
        print_success "All files downloaded successfully"
        return 0
    else
        print_error "Some files failed to download"
        return 1
    fi
}

# Install Python dependencies for skill scripts
install_python_deps() {
    print_header "Installing Python Dependencies"

    local requirements_file="${LOCAL_SKILL_DIR}/scripts/requirements.txt"

    if [ ! -f "$requirements_file" ]; then
        print_error "Requirements file not found: $requirements_file"
        return 1
    fi

    if command -v uv &> /dev/null; then
        print_step "Using uv to install dependencies"
        uv pip install -r "$requirements_file"
        print_success "Dependencies installed with uv"
    elif command -v pip &> /dev/null; then
        print_step "Using pip to install dependencies"
        pip install -r "$requirements_file"
        print_success "Dependencies installed with pip"
    else
        print_error "Neither uv nor pip found. Cannot install Python dependencies."
        return 1
    fi
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"

    local required_files=(
        "SKILL.md"
        "reference/python_mcp_server.md"
        "reference/mcp_best_practices.md"
        "scripts/evaluation.py"
    )

    local all_present=true

    for file in "${required_files[@]}"; do
        if [ -f "${LOCAL_SKILL_DIR}/${file}" ]; then
            print_success "Found: ${file}"
        else
            print_error "Missing: ${file}"
            all_present=false
        fi
    done

    if $all_present; then
        print_success "Installation verified"
        return 0
    else
        print_error "Installation verification failed"
        return 1
    fi
}

# Generate installation report
generate_report() {
    print_header "Installation Report"

    echo -e "${GREEN}mcp-builder skill installed successfully!${NC}\n"
    echo "Location: ${LOCAL_SKILL_DIR}"
    echo ""
    echo "Available references:"
    echo "  - reference/python_mcp_server.md     (Python MCP guide)"
    echo "  - reference/mcp_best_practices.md    (Best practices)"
    echo "  - reference/evaluation.md            (Evaluation guide)"
    echo "  - reference/node_mcp_server.md       (Node.js MCP guide)"
    echo ""
    echo "Available scripts:"
    echo "  - scripts/evaluation.py              (Evaluation script)"
    echo "  - scripts/connections.py             (Connection utilities)"
    echo ""
    echo "Usage in Claude Code:"
    echo "  The skill is now available locally in your project."
    echo "  Claude Code will automatically detect it in .claude/skills/"
    echo ""

    if $INSTALL_DEPS; then
        echo -e "${GREEN}Python dependencies installed${NC}"
        echo "You can now run: python ${LOCAL_SKILL_DIR}/scripts/evaluation.py"
        echo ""
    else
        echo -e "${YELLOW}To install Python dependencies, run:${NC}"
        echo "  $0 --install-deps"
        echo ""
    fi
}

# Update .gitignore if needed
update_gitignore() {
    print_header "Updating .gitignore"

    local gitignore_file=".gitignore"
    local patterns=(
        ".claude/skills/**/node_modules/"
        ".claude/skills/**/__pycache__/"
        ".claude/skills/**/*.pyc"
    )

    if [ ! -f "$gitignore_file" ]; then
        print_info "No .gitignore found, creating one"
        touch "$gitignore_file"
    fi

    local added_count=0
    for pattern in "${patterns[@]}"; do
        if ! grep -qF "$pattern" "$gitignore_file"; then
            echo "$pattern" >> "$gitignore_file"
            print_success "Added to .gitignore: $pattern"
            ((added_count++))
        fi
    done

    if [ $added_count -eq 0 ]; then
        print_info ".gitignore already up to date"
    else
        print_success "Updated .gitignore with $added_count patterns"
    fi
}

# Main execution
main() {
    print_header "MCP-Builder Skill Installer"

    if $UPDATE_MODE; then
        print_info "Running in UPDATE mode"
    else
        print_info "Running in INSTALL mode"
    fi

    # Step 1: Check dependencies
    check_dependencies

    # Step 2: Create directories
    create_directories

    # Step 3: Download skill files
    if ! download_skill_files; then
        print_error "Installation failed during file download"
        exit 1
    fi

    # Step 4: Update .gitignore
    update_gitignore

    # Step 5: Verify installation
    if ! verify_installation; then
        print_error "Installation verification failed"
        exit 1
    fi

    # Step 6: Install Python dependencies if requested
    if $INSTALL_DEPS; then
        install_python_deps
    fi

    # Step 7: Generate report
    generate_report

    print_header "Installation Complete"
    print_success "mcp-builder skill ready to use!"
}

# Run main function
main
