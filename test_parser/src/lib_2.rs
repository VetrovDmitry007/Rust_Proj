use pyo3::prelude::*;
use http_bytes;
use http_bytes::http::HeaderMap;
use std::str;
use httparse::Header;
use pyo3::types::{PyByteArray, PyBytes, PyList};
use pyo3::Python;


#[pyclass]
#[derive(Clone, Debug)]
struct ResponseParser {
    status: String,
    headers: HeaderMap,
    body: String,
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
        }
    }

    pub fn execute(&mut self, a_resp: &[u8])-> PyResult<()> {
        let mut headers_buffer: Vec<Header<'_>> = vec![http_bytes::EMPTY_HEADER; 20];
        let (r, b) = http_bytes::parse_response_header(
            a_resp,
            &mut headers_buffer,
            ).unwrap().unwrap();
        self.status = r.status().to_string();
        self.headers = (*r.headers()).clone().into();
        self.body = str::from_utf8(&b).unwrap().into();
        println!("Length body: {}", self.body.len());
        Ok(())
    }

    pub fn get_status_code(&mut self)-> PyResult<String>{
        Ok(self.status.to_string())
    }

    pub fn get_headers(&mut self, py: Python<'_>)-> Py<PyList>{
        let mut elements: Vec<(String, String)> = vec![];
        for (key, value) in self.headers.iter() {
            elements.push(  (key.to_string(), value.to_str().unwrap().to_string())         );
        }
        let list: Py<PyList> = PyList::new(py, elements.clone()).into();
        return list;
    }

    pub fn get_body(&mut self)-> PyResult<String>{
        Ok(self.body.to_string())
    }
}

#[pymodule]
fn test_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ResponseParser>()?;
    Ok(())
}
