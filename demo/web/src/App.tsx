import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import Home from '@/pages/Home';
import MarketInsight from '@/pages/MarketInsight';
import SmartSelection from '@/pages/SmartSelection';
import SupplyChain from '@/pages/SupplyChain';
import ContentGeneration from '@/pages/ContentGeneration';
import Compliance from '@/pages/Compliance';
import CustomerService from '@/pages/CustomerService';
import PolicyReplication from '@/pages/PolicyReplication';
import Pipeline from '@/pages/Pipeline';
import Pricing from '@/pages/Pricing';
import Login from '@/pages/Login';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/market-insight" element={<MarketInsight />} />
            <Route path="/smart-selection" element={<SmartSelection />} />
            <Route path="/supply-chain" element={<SupplyChain />} />
            <Route path="/content-generation" element={<ContentGeneration />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/customer-service" element={<CustomerService />} />
            <Route path="/policy-replication" element={<PolicyReplication />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/login" element={<Login />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
