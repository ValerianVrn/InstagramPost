import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

function LoadingButton(props) {
  const { isLoading, className = '', children, ...rest } = props;

  return (
    <button className={`loading-button ${className}`} disabled={isLoading} type="submit" {...rest}
    >
      {isLoading && (
        <FontAwesomeIcon icon={faSpinner} spin className="loading-icon" />
      )}
      {children}
    </button>
  );
}

export default LoadingButton;
