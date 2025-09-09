package main

import (
	"log"
	"time"

	jwt "github.com/dgrijalva/jwt-go"
)

// backgroundJob simulates reachable vulnerability in worker path
func backgroundJob() {
	tokenStr := "malformed.token.string"
	// Vulnerable parse path in background job
	_, _ = jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		return []byte("secret"), nil
	})
}

func main() {
	log.Println("worker starting")
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()
	for i := 0; i < 1; i++ { // run once for demo
		<-ticker.C
		backgroundJob()
	}
	log.Println("worker done")
}
