// extern crate http;
extern crate native_tls;

//use http::{Response, StatusCode};
use native_tls::HandshakeError::{Failure, WouldBlock};
use native_tls::{Identity, TlsAcceptor, TlsStream};
use std::fs::File;
use std::io::Read;
use std::io::Write;
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::thread;

fn main() {
    let mut file = File::open("/Users/john/Documents/ssl/certs/identity.pfx").unwrap();
    let mut identity = vec![];
    file.read_to_end(&mut identity).unwrap();
    let identity = Identity::from_pkcs12(&identity, "BBwQd4CQWH7u4DH").unwrap();

    let acceptor = TlsAcceptor::new(identity).unwrap();
    let acceptor = Arc::new(acceptor);

    let listener = TcpListener::bind("localhost:4433").unwrap();

    fn handle_client(mut stream: TlsStream<TcpStream>) -> std::io::Result<usize> {
        let mut buf = Vec::<u8>::with_capacity(1024);
        stream.read_to_end(&mut buf)?;
        //let response = Response::builder().status(StatusCode::OK).body(()).unwrap();

        stream.write("HTTP/1.1 200 OK\n".as_bytes())?;
        stream.write("Content-Type: text/html\n".as_bytes())?;
        stream.write("Content-Length: 13\n".as_bytes())?;
        stream.write("\n".as_bytes())?;
        stream.write("<h1>Test</h1>\n".as_bytes())

        // for (key, value) in response.headers().into_iter() {
        //     stream.write(&key.as_str().as_bytes()).unwrap();
        //     stream.write(" ".as_bytes()).unwrap();
        //     stream.write(&value.to_str().unwrap().as_bytes()).unwrap();
        // }

        // stream.flush().unwrap();
        // stream.shutdown().unwrap();
    }

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                let acceptor = acceptor.clone();
                thread::spawn(move || match acceptor.accept(stream) {
                    Ok(stream) => match handle_client(stream) {
                        Ok(_) => println!("Success"),
                        Err(e) => println!("{}", e),
                    },
                    Err(e) => match e {
                        WouldBlock(_) => println!("WouldBlock"),
                        Failure(e) => println!("{}", e),
                    },
                });
            }
            Err(_) => { /* connection failed */ }
        }
    }
}
// extern crate tiny_http;
// use tiny_http::{Response, Server};

// #[cfg(not(feature = "tiny_http.ssl"))]
// fn main() {
//     println!("This example requires the `ssl` feature to be enabled");
// }

// #[cfg(feature = "tiny_http.ssl")]
// fn main() {
//     let server = Server::https(
//         "127.0.0.1:8080",
//         tiny_http::SslConfig {
//             certificate: include_bytes!("/Users/john/Documents/ssl/server.crt").to_vec(),
//             private_key: include_bytes!("/Users/john/Documents/ssl/server.key").to_vec(),
//         },
//     )
//     .unwrap();

//     for request in server.incoming_requests() {
//         assert!(request.secure());
//         println!(
//             "received request! method: {:?}, url: {:?}, headers: {:?}",
//             request.method(),
//             request.url(),
//             request.headers()
//         );
//         let response = Response::from_string("hello world");
//         request.respond(response).unwrap();
//     }
// }
