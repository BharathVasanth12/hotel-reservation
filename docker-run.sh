#!/bin/bash

# Hotel Reservation Docker Build & Run Script
# Works with both Docker and Podman

set -e

# Detect container runtime
if command -v docker &> /dev/null; then
    RUNTIME="docker"
elif command -v podman &> /dev/null; then
    RUNTIME="podman"
else
    echo "❌ Neither Docker nor Podman found. Please install one of them."
    exit 1
fi

echo "🐳 Using container runtime: $RUNTIME"

# Configuration
IMAGE_NAME="hotel-reservation"
IMAGE_TAG="latest"
CONTAINER_NAME="hotel-reservation-app"
HOST_PORT="5001"
CONTAINER_PORT="5001"

# Functions
build_image() {
    echo "🏗️  Building Docker image..."
    $RUNTIME build -t ${IMAGE_NAME}:${IMAGE_TAG} .
    echo "✅ Image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}"
}

run_container() {
    echo "🚀 Starting container..."
    
    # Stop and remove existing container if running
    if $RUNTIME ps -a | grep -q $CONTAINER_NAME; then
        echo "⚠️  Stopping existing container..."
        $RUNTIME stop $CONTAINER_NAME 2>/dev/null || true
        $RUNTIME rm $CONTAINER_NAME 2>/dev/null || true
    fi
    
    # Run new container
    $RUNTIME run -d \
        --name $CONTAINER_NAME \
        -p ${HOST_PORT}:${CONTAINER_PORT} \
        -v $(pwd)/artifacts:/app/artifacts:ro \
        ${IMAGE_NAME}:${IMAGE_TAG}
    
    echo "✅ Container started successfully!"
    echo "📊 Access the app at: http://localhost:${HOST_PORT}"
}

stop_container() {
    echo "🛑 Stopping container..."
    $RUNTIME stop $CONTAINER_NAME
    $RUNTIME rm $CONTAINER_NAME
    echo "✅ Container stopped and removed"
}

show_logs() {
    echo "📋 Showing container logs (Ctrl+C to exit)..."
    $RUNTIME logs -f $CONTAINER_NAME
}

show_status() {
    echo "📊 Container Status:"
    $RUNTIME ps -a | grep $CONTAINER_NAME || echo "Container not running"
    echo ""
    echo "🖼️  Images:"
    $RUNTIME images | grep $IMAGE_NAME || echo "No images found"
}

show_health() {
    echo "🏥 Health Check:"
    curl -s http://localhost:${HOST_PORT}/health | python -m json.tool || echo "Service not responding"
}

cleanup() {
    echo "🧹 Cleaning up..."
    $RUNTIME stop $CONTAINER_NAME 2>/dev/null || true
    $RUNTIME rm $CONTAINER_NAME 2>/dev/null || true
    $RUNTIME rmi ${IMAGE_NAME}:${IMAGE_TAG} 2>/dev/null || true
    echo "✅ Cleanup complete"
}

# Main menu
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    start)
        build_image
        run_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        stop_container
        run_container
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    health)
        show_health
        ;;
    cleanup)
        cleanup
        ;;
    help|*)
        echo "Hotel Reservation Docker Management Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build      - Build the Docker image"
        echo "  run        - Run the container"
        echo "  start      - Build and run (complete setup)"
        echo "  stop       - Stop and remove the container"
        echo "  restart    - Restart the container"
        echo "  logs       - Show container logs"
        echo "  status     - Show container and image status"
        echo "  health     - Check application health"
        echo "  cleanup    - Remove container and image"
        echo "  help       - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start        # Build and run everything"
        echo "  $0 logs         # View application logs"
        echo "  $0 health       # Check if app is running"
        echo "  $0 cleanup      # Remove everything"
        ;;
esac
