// File: html/ui/static/js/config.js
// This file is used to configure the application.
// It is loaded before the application starts.

// window.apiBaseUrl = "http://localhost:8000/";
// window.webSocketBaseUrl = "ws://localhost:8000/ws";

window.apiBaseUrl = `${window.location.protocol}//${window.location.hostname}:8000/`;
window.webSocketBaseUrl = `ws://${window.location.hostname}:8000/ws`;

