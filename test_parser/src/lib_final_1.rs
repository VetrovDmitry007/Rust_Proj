use pyo3::prelude::*;
use http_bytes;
use http_bytes::http::HeaderMap;
use std::str;
use httparse::Header;
use pyo3::types::{PyByteArray, PyBytes, PyDict};
use pyo3::Python;



#[pyclass]
#[derive(Clone, Debug)]
struct ResponseParser {
    status: String,
    headers: HeaderMap,
    body: String,
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
           status: "400".to_string(),
           headers: HeaderMap::new(),
           body: "".to_string(),
           fl_msg_complete: false,
           buffer: vec![0u8; 0],
        }
    }

    pub fn execute(&mut self, a_resp: &[u8], eof_mark: &[u8])-> PyResult<()> {
        self.buffer.extend(a_resp.to_vec().iter().cloned());
        let b_resp: &[u8] = &self.buffer.clone();
        //let с_resp: &[u8] = &self.buffer.clone();
        //Проверка конца пакета на наличие eof_mark
        if !eof_mark.is_empty(){
            // Параметр eof_mark задан, eof_mark в конце пакета
            let is_eof_mark = b_resp.ends_with(eof_mark);
            if is_eof_mark{
                self.parser(b_resp)
            }
        } else {
            // Параметр eof_mark НЕ задан
            // Нахождение content-lengt
            let len_c: i32 = self.content_len(b_resp);
            // Нахождение Lengt body
            let len_d: i32 = self.get_body_len(b_resp);
            if (len_c == len_d) & (len_c > 0){
                self.parser(b_resp);
            }
            if (len_c == 0) & (len_d > 0){
                self.fl_msg_complete = true;
            }
        }
        Ok(())
    }

    fn parser(&mut self, b_resp:&[u8]){
        let mut headers_buffer: Vec<Header<'_>> = vec![http_bytes::EMPTY_HEADER; 20];
        let (r, b) = http_bytes::parse_response_header(
            b_resp,
            &mut headers_buffer,
            ).unwrap().unwrap();
        let s = r.status().to_string();
        let parts: Vec<&str> = s.split_whitespace().collect();
        let n: i32 = parts[0].parse().unwrap();
        self.status = n.to_string();
        self.headers = (*r.headers()).clone().into();
        self.body = str::from_utf8(&b).unwrap().into();
        self.fl_msg_complete = true;
    }

    // Нахождения размер Body в байтах
    fn get_body_len(&mut self, response:&[u8]) -> i32{
        let index = response.windows(4).position(|window| window == b"\r\n\r\n");
        let size = match index {
            Some(i) => response.len() - i - 4,
            None => 0,
        };
        return size.try_into().unwrap();
    }

     // Нахождение значения строки -- content-lengt: 162
    fn content_len(&mut self, s:&[u8]) -> i32{
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

    pub fn get_status_code(&mut self)-> PyResult<String>{
        Ok(self.status.to_string())
    }

    pub fn get_headers(&mut self, py: Python<'_>)-> Py<PyDict>{
        let res_dict: &PyDict = PyDict::new(py);
        for (key, value) in self.headers.iter() {
            res_dict.set_item(key.to_string(), value.to_str().unwrap().to_string()).unwrap()
        }
        return res_dict.into();
    }

    pub fn recv_body(&mut self)-> PyResult<&[u8]>{
        Ok(self.body.as_bytes())
    }

    pub fn is_message_complete(&mut self) -> bool {
        self.fl_msg_complete
    }


}

#[pymodule]
fn test_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ResponseParser>()?;
    Ok(())
}
