import React from 'react';

import './Nav.scss';

const Nav: React.FC = () => {
  return (
    <nav className="nav">
      <span className="nav-item">Home</span>
      <div className="nav-spacer">|</div>
      <span className="nav-item">About</span>
      <div className="nav-spacer">|</div>
      <span className="nav-item">Contact</span>
    </nav>
  );
};

export default Nav;