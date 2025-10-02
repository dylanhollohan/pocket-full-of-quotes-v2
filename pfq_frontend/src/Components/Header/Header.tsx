import React from 'react';

import './Header.scss';

import philosopher from '../../assets/philosopher.png';

const Header: React.FC = () => {
  return (
    <header className="header">
      <img src={philosopher} alt="Logo" className="logo" />
      <h1 className="title">Pocket Full of Quotes</h1>
      <span className="login">Log In placeholder</span>
    </header>
  );
};

export default Header;