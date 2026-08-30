use std::ffi::CStr;
use std::os::raw::c_char;


#[unsafe(no_mangle)]
pub extern "C" fn validate_gcode_line(raw_line: *const c_char) -> bool {
    if raw_line.is_null() {
        return false;
    }

    let c_str = unsafe { CStr::from_ptr(raw_line) };
    let line_str = match c_str.to_str() {
        Ok(s) => s.trim(),
        Err(_) => return false, 
    };

    if line_str.is_empty() || line_str.len() > 256 {
        return false;
    }

    if let Some(first_char) = line_str.chars().next() {
        match first_char.to_ascii_uppercase() {
            'G' | 'M' | 'X' | 'Y' | 'Z' | 'F' | 'S' => true, 
            _ => false, 
        }
    } else {
        false
    }
}
