import React from 'react';

import { fakeDB } from '../../Data/fake-db';

import './Home.scss';


const Home: React.FC = () => {
  return (
    <section className="home">
      <h2>My Favorites</h2>
      { fakeDB.map(quote => (
        <div key={quote.id} className="card">
          <p className="quote">"{quote.quote}"</p>
          <p className="author">- {quote.author}</p>
        </div>
      )) 
      }
    </section>
  );
};

export default Home;