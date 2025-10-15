import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AppContextType {
  currentLocation: string;
  setCurrentLocation: (location: string) => void;
  currentUserLdap: string | null;
  setCurrentUserLdap: (ldap: string | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [currentLocation, setCurrentLocation] = useState<string>('san_jose');
  const [currentUserLdap, setCurrentUserLdap] = useState<string | null>(null);

  return (
    <AppContext.Provider
      value={{
        currentLocation,
        setCurrentLocation,
        currentUserLdap,
        setCurrentUserLdap,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};