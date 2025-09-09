module example.com/noisecutter-go-multi-entry

go 1.21

require (
	github.com/dgrijalva/jwt-go v3.2.0+incompatible // CVE-2020-26160 (OSV: GO-2020-0015)
	github.com/gorilla/mux v1.8.0
)
