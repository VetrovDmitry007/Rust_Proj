use pyo3::prelude::*;
use http_bytes;
use http_bytes::http::HeaderMap;
use std::str;
use httparse::Header;
use pyo3::types::{PyByteArray, PyBytes, PyList};
use pyo3::Python;
// use http::HeaderValue;


#[pyclass]
#[derive(Clone, Debug)]
struct ResponseParser {
    status: String,
    headers: HeaderMap,
    body: String,
    len_content: usize,
    len_body: usize,
    fl_msg_complete: bool,
    buffer: Vec<u8>,
}

#[derive(FromPyObject)]
enum PyData<'a> {
    Bytes(&'a PyBytes),
    ByteArray(&'a PyByteArray),
}

#[pymethods]
impl ResponseParser {
    #[new]
    fn py_new() -> Self {
        ResponseParser {
           status: "".to_string(),
           headers: HeaderMap::new(),
           body: "".to_string(),
           len_content: 0,
           len_body: 0,
           fl_msg_complete: false,
           buffer: vec![0u8; 0],
        }
    }

    pub fn execute(&mut self, a_resp: &[u8])-> PyResult<()> {
        self.buffer.extend(a_resp.to_vec().iter().cloned());
        let b_resp: &[u8] = &self.buffer;

        let mut headers_buffer: Vec<Header<'_>> = vec![http_bytes::EMPTY_HEADER; 20];
        let (r, b) = http_bytes::parse_response_header(
            b_resp,
            &mut headers_buffer,
            ).unwrap().unwrap();
        self.status = r.status().to_string();
        self.headers = (*r.headers()).clone().into();
        self.body = str::from_utf8(&b).unwrap().into();

        let _ = self.upd_msg_complete();
        Ok(())
    }

    //Находим значение content-length
    fn get_length_content(&mut self) -> usize {
    if !self.headers.contains_key("content-length") {
        return 0;
    }
    let value = self.headers.get("content-length").expect("REASON").to_str().unwrap();
    let num: i32 = value.parse().unwrap();
    return num.try_into().unwrap();
    }

    pub fn get_status_code(&mut self)-> PyResult<String>{
        Ok(self.status.to_string())
    }

    pub fn get_headers(&mut self, py: Python<'_>)-> Py<PyList>{
        let mut elements: Vec<(String, String)> = vec![];
        for (key, value) in self.headers.iter() {
            elements.push(  (key.to_string(), value.to_str().unwrap().to_string())        );
        }
        let list: Py<PyList> = PyList::new(py, elements.clone()).into();
        return list;
    }

    pub fn recv_body(&mut self)-> PyResult<String>{
        Ok(self.body.to_string())
    }

    pub fn is_message_complete(&mut self) -> bool {
        self.fl_msg_complete
    }

    fn upd_msg_complete(&mut self) -> PyResult<()> {
        self.len_content = self.get_length_content();
        self.len_body = self.body.len();
        println!("Content-length : {}", self.len_content.to_string());
        println!("Length body: {}", self.body.len());

        if self.len_content.eq(&self.len_body) && self.len_body > 0{
            self.fl_msg_complete = true;
        } else {
            self.fl_msg_complete = false;
        }
        Ok(())
    }

    pub fn is_partial_body(&mut self) -> bool {
        self.len_body > 0
    }


}

#[pymodule]
fn test_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ResponseParser>()?;
    Ok(())
}
