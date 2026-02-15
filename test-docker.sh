#!/bin/bash
# Test runner script for jetq across multiple Python versions using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [PYTHON_VERSION]

Run jetq tests in Docker containers across multiple Python versions.

OPTIONS:
    -a, --all           Run tests on all Python versions (3.8-3.13)
    -b, --build         Build Docker images before running tests
    -c, --clean         Clean up Docker containers and images
    -s, --shell VERSION Open a shell in the specified Python version container
    -h, --help          Display this help message

PYTHON_VERSION:
    3.8, 3.9, 3.10, 3.11, 3.12, 3.13, or 'all'

EXAMPLES:
    $0 3.8              # Run tests on Python 3.8
    $0 --all            # Run tests on all Python versions
    $0 --build 3.10     # Build and run tests on Python 3.10
    $0 --shell 3.9      # Open a shell in Python 3.9 container
    $0 --clean          # Clean up all Docker resources

EOF
}

# Function to build Docker image
build_image() {
    local version=$1
    print_info "Building Docker image for Python ${version}..."
    docker compose build "test-py${version//./}"
    print_success "Built image for Python ${version}"
}

# Function to run tests for a specific version
run_tests() {
    local version=$1
    local service_name="test-py${version//./}"
    
    print_info "Running tests on Python ${version}..."
    
    if docker compose run --rm "$service_name"; then
        print_success "Python ${version} tests passed ✓"
        return 0
    else
        print_error "Python ${version} tests failed ✗"
        return 1
    fi
}

# Function to run tests on all versions
run_all_tests() {
    local failed_versions=()
    local versions=("3.8" "3.9" "3.10" "3.11" "3.12" "3.13")
    
    print_info "Running tests on all Python versions..."
    echo ""
    
    for version in "${versions[@]}"; do
        if ! run_tests "$version"; then
            failed_versions+=("$version")
        fi
        echo ""
    done
    
    echo "==============================================="
    if [ ${#failed_versions[@]} -eq 0 ]; then
        print_success "All tests passed across all Python versions! 🎉"
        return 0
    else
        print_error "Tests failed on Python versions: ${failed_versions[*]}"
        return 1
    fi
}

# Function to open shell in container
open_shell() {
    local version=$1
    local service_name="test-py${version//./}"
    
    print_info "Opening shell in Python ${version} container..."
    docker compose run --rm "$service_name" /bin/bash
}

# Function to clean up Docker resources
cleanup() {
    print_info "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker compose down --remove-orphans
    
    # Remove images
    docker images | grep "jetq-test" | awk '{print $3}' | xargs -r docker rmi -f
    
    print_success "Cleanup complete"
}

# Main script logic
main() {
    local build_flag=false
    local version=""
    local action="test"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker compose &> /dev/null; then
        print_error "docker compose is not installed. Please install docker compose first."
        exit 1
    fi
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--all)
                version="all"
                shift
                ;;
            -b|--build)
                build_flag=true
                shift
                ;;
            -c|--clean)
                cleanup
                exit 0
                ;;
            -s|--shell)
                action="shell"
                version="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            3.8|3.9|3.10|3.11|3.12|3.13)
                version="$1"
                shift
                ;;
            all)
                version="all"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # If no version specified, default to all
    if [ -z "$version" ]; then
        version="all"
    fi
    
    # Build images if requested
    if [ "$build_flag" = true ]; then
        if [ "$version" = "all" ]; then
            print_info "Building all images..."
            docker compose build
        else
            build_image "$version"
        fi
    fi
    
    # Execute action
    if [ "$action" = "shell" ]; then
        open_shell "$version"
    elif [ "$version" = "all" ]; then
        run_all_tests
    else
        run_tests "$version"
    fi
}

# Run main function
main "$@"
