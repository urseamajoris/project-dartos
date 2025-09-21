import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Tabs, Tab, Box } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import DescriptionIcon from '@mui/icons-material/Description';
import DashboardIcon from '@mui/icons-material/Dashboard';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleChange = (event, newValue) => {
    navigate(newValue);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
      <Tabs value={location.pathname} onChange={handleChange} aria-label="navigation tabs">
        <Tab 
          icon={<HomeIcon />} 
          label="Home" 
          value="/" 
        />
        <Tab 
          icon={<DescriptionIcon />} 
          label="Documents" 
          value="/documents" 
        />
        <Tab 
          icon={<DashboardIcon />} 
          label="Dashboard" 
          value="/dashboard" 
        />
      </Tabs>
    </Box>
  );
}

export default Navigation;