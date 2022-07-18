package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/spf13/pflag"
)

type Server struct {
	port     int
	code     int
	redirect string
	freeze   bool
}

func (s Server) Index(w http.ResponseWriter, r *http.Request) {
	if s.freeze {
		time.Sleep(60 * time.Second)
	}
	if s.redirect != "" {
		http.Redirect(w, r, s.redirect, s.code)
		return
	}
	w.WriteHeader(s.code)
	fmt.Fprintf(w, "It Works!\n")
}

func main() {
	s := Server{}
	pflag.IntVar(&s.port, "port", 1945, "the port to listen")
	pflag.IntVar(&s.code, "code", 200, "HTTP status code to return")
	pflag.StringVar(&s.redirect, "redirect", "", "URL to redirect to")
	pflag.BoolVar(&s.freeze, "freeze", false, "freeze for all requests")
	pflag.Parse()

	http.HandleFunc("/", s.Index)
	addr := fmt.Sprintf("0.0.0.0:%d", s.port)
	fmt.Printf("listening on http://%s/\n", addr)
	err := http.ListenAndServe(addr, nil)
	if err != nil {
		log.Fatalln(err)
	}
}
