use std::ffi::CStr;
use std::os::raw::c_char;

// Отключаем изменение имени функции компилятором для связи с C++
#[unsafe(no_mangle)]
pub extern "C" fn validate_gcode_line(raw_line: *const c_char) -> bool {
    if raw_line.is_null() {
        return false;
    }

    // Безопасно переводим сырой указатель C++ в строку Rust
    let c_str = unsafe { CStr::from_ptr(raw_line) };
    let line_str = match c_str.to_str() {
        Ok(s) => s.trim(),
        Err(_) => return false, // Если в кабеле прилетели битые байты
    };

    // Защита от переполнения буфера в C++ (длина строки строго до 256 символов)
    if line_str.is_empty() || line_str.len() > 256 {
        return false;
    }

    // Проверяем первый символ: строка должна начинаться с валидной команды ЧПУ
    if let Some(first_char) = line_str.chars().next() {
        match first_char.to_ascii_uppercase() {
            'G' | 'M' | 'X' | 'Y' | 'Z' | 'F' | 'S' => true, // Строка безопасна!
            _ => false, // Неизвестный или опасный символ — блокируем!
        }
    } else {
        false
    }
}
