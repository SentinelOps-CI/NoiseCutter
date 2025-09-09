package main

import (
	"fmt"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "ok")
	})

	// Note: the vulnerable transitive dep (e.g., websocket) is not referenced at runtime
	// to demonstrate unreachable advisory suppression.

	_ = mux
}
