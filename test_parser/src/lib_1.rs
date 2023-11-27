use pyo3::prelude::*;
use http_bytes;
use std::str;
use httparse::Header;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Serialize, Deserialize, Clone, Debug)]
struct ParsResponse {
    #[pyo3(get)]
    status: String,
    #[pyo3(get)]
    headers: String,
    #[pyo3(get)]
    body: String,
}


#[pyfunction]
fn get_pars(a_resp: &[u8]) -> PyResult<Option<ParsResponse>>{

    let mut b_resp:&[u8]= b"HTTP/1.1 200 OK\r\n\nHost: example.com\r\n\nContent-Type: text/plain\r\n \r\n\nHello, world\n";
    //println!("a_resp: {}", str::from_utf8(&a_resp).unwrap());
    //println!("{}", "------------------------");
    //println!("b_resp: {}", str::from_utf8(&b_resp).unwrap());

    let mut headers_buffer: Vec<Header<'_>> = vec![http_bytes::EMPTY_HEADER; 20];
    let (r, b) = http_bytes::parse_response_header(
        a_resp,
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
    //Ok(str_headers.to_string())

    Ok(Some(res_parser))



}

#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}




#[pymodule]
fn test_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(get_pars, m)?)?;
    Ok(())
}
