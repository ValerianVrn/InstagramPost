import React, { useRef } from 'react';

function AutoResizeTextArea(props) {
  const { value, onChange, placeholder, minHeight } = props;

  const textAreaRef = useRef(null);

  const handleChange = (event) => {
    if (onChange) {
      onChange(event);
    }

    if (textAreaRef.current) {
      textAreaRef.current.style.height = `${minHeight}px`;
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`;
    }
  };

  return (
    <textarea
      ref={textAreaRef}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      style={{ minHeight }}
    />
  );
}

export default AutoResizeTextArea;
