import { useNavigate } from 'react-router-dom';
import './header.css';

const Header = () => {
    const navigate = useNavigate();
    
    return (
        <header className='header'>
            <h1 className='header-title' onClick={() => navigate('/')}>SCISTU25</h1>
            <div className="header-icons">
                <div className="icon-container">
                    <i className="fa-solid fa-gear"></i>
                </div>
                <div className="icon-container">
                    <i className="fa-solid fa-bars"></i>
                </div>
                <div className="icon-container">
                    <i className="fa-solid fa-circle-user"></i>
                </div>
            </div>
        </header>
    );
}

export default Header;