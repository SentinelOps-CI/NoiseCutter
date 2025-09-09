package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	jwt "github.com/dgrijalva/jwt-go"
	"github.com/gorilla/mux"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("ok"))
}

func noopHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNoContent)
}

// doRisky demonstrates a reachable vulnerable usage path
func doRiskyHandler(w http.ResponseWriter, r *http.Request) {
	tokenStr := r.URL.Query().Get("token")
	if tokenStr == "" {
		tokenStr = "malformed.token.string"
	}
	// Vulnerable: Parse without key validation may be abused (demo)
	_, _ = jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		return []byte("secret"), nil
	})
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("did risky"))
}

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/health", healthHandler).Methods("GET")
	r.HandleFunc("/noop", noopHandler).Methods("GET")
	r.HandleFunc("/do-risky", doRiskyHandler).Methods("POST", "GET")

	addr := ":8080"
	if p := os.Getenv("PORT"); p != "" {
		addr = fmt.Sprintf(":%s", p)
	}
	log.Printf("server listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, r))
}
