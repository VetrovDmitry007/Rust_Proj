use http_bytes;
use std::str;
use httparse::Header;
use serde::{Deserialize, Serialize};


#[derive(Serialize, Deserialize, Debug)]
struct ParsResponse {
    status: String,
    headers: String,
    body: String,
}


fn main() {

    let b_resp:&[u8]= b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Type: text/plain\r\n\r\nHello, world\n";
    //let b_resp:&[u8]= b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Ty/pla\r\n\r\n";

    let mut headers_buffer: Vec<Header<'_>> = vec![http_bytes::EMPTY_HEADER; 20];
    let (r, b) = http_bytes::parse_response_header(
        b_resp,
        &mut headers_buffer,
        ).unwrap().unwrap();
    
    let str_headers: String = format!("{:?}", r.headers()).into();

    // Serialize a struct to JSON
    let res_parser: ParsResponse = ParsResponse {
        status: r.status().as_str().into(),
        headers: str_headers.clone(),
        body: str::from_utf8(&b).unwrap().into(),
    };
     

    //println!("Parser response: {:?}", res_parser);
    //println!("Status: {}", r.status());
    //println!("Headers: {}", str_headers);
    //println!("Body: {}", str::from_utf8(&b).unwrap());

    let s: &[u8]=  b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\nHello, world\n";
    let n: i32 = content_len(s);
    //println!("cont_len = {}", n);
    let cn_b: i32 = get_body_len(s);
    println!("body_len = {}", cn_b);

}

// Нахождения размер Body в байтах
fn get_body_len(response:&[u8]) -> i32{
    //let response = b"HTTP/1.1 301 Moved Permanently\r\nConnection: keep-alive\r\nContent-Length: 162\r\nServer: GitHub.com\r\nContent-Type: text/html\r\nLocation: https://gunicorn.org/\r\nX-GitHub-Request-Id: 6642:9CFC:8BD6E9:8DF453:65622067\r\nAccept-Ranges: bytes\r\nDate: Sat, 25 Nov 2023 16:27:19 GMT\r\nVia: 1.1 varnish\r\nAge: 0\r\nX-Served-By: cache-fra-eddf8230071-FRA\r\nX-Cache: MISS\r\nX-Cache-Hits: 0\r\nX-Timer: S1700929639.243087,VS0,VE95\r\nVary: Accept-Encoding\r\nX-Fastly-Request-ID: a1ad7303c7f7029492e0f15b1a51d1c557942c39\r\n\r\n<html>\r\n<head><title>301 Moved Permanently</title></head>\r\n<body>\r\n<center><h1>301 Moved Permanently</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n";
    //let response = b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\nHello, world\n";
    let index = response.windows(4).position(|window| window == b"\r\n\r\n");
    let size = match index {
        Some(i) => response.len() - i - 4,
        None => 0,
    };
    //println!("Size in bytes: {}", size)
    return size.try_into().unwrap();
}

 // Нахождение значения строки -- content-lengt: 162
fn content_len(s:&[u8]) -> i32{    
    //let s: &[u8]=  b"HTTP/1.1 200 OK\r\nHost: example.com\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\nHello, world\n";
    let content_length = std::str::from_utf8(&s)
        .unwrap()
        .split("\r\n")
        .find(|&x| x.contains("Content-Length"))
        .unwrap_or("");
    
    if content_length.len() > 0{
        let parts: Vec<&str> = content_length.split_whitespace().collect();
        let n: i32 = parts[1].parse().unwrap();
        return n;

    }
    return 0;
}