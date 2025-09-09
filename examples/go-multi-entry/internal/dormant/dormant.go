package dormant

import (
	jwt "github.com/dgrijalva/jwt-go"
)

// Unused demonstrates an imported vulnerable dependency path
// that remains unreachable from server and worker.
func Unused() string {
	tokenStr := "unused.token"
	_, _ = jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		return []byte("secret"), nil
	})
	return "noop"
}
