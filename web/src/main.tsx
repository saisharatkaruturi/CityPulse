import './styles/tokens.css';

import { StrictMode, lazy, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AppHome, NotFound, RequireRoute } from './app/guards';
import { AuthProvider } from './auth';
import { LocaleProvider } from './i18n';
import Landing from './landing/Landing';
import { MetaProvider } from './meta';

const Shell = lazy(() => import('./app/Shell'));
const SignIn = lazy(() => import('./app/SignIn'));
const SignUp = lazy(() => import('./app/SignUp'));
const MyReports = lazy(() => import('./app/pages/MyReports'));
const NewReport = lazy(() => import('./app/pages/NewReport'));
const ReportDetail = lazy(() => import('./app/pages/ReportDetail'));
const Services = lazy(() => import('./app/pages/Services'));
const Notifications = lazy(() => import('./app/pages/Notifications'));
const Queue = lazy(() => import('./app/pages/Queue'));
const Analytics = lazy(() => import('./app/pages/Analytics'));

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LocaleProvider>
      <MetaProvider>
        <AuthProvider>
          <BrowserRouter>
            <Suspense fallback={null}>
              <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/signin" element={<SignIn />} />
                <Route path="/signup" element={<SignUp />} />
                <Route path="/app" element={<Shell />}>
                  <Route index element={<AppHome resident={<MyReports />} />} />
                  <Route path="report" element={<RequireRoute route="report"><NewReport /></RequireRoute>} />
                  <Route path="reports/:id" element={<RequireRoute route="reportDetail"><ReportDetail /></RequireRoute>} />
                  <Route path="services" element={<RequireRoute route="services"><Services /></RequireRoute>} />
                  <Route path="services/:code" element={<RequireRoute route="services"><Services /></RequireRoute>} />
                  <Route path="notifications" element={<RequireRoute route="notifications"><Notifications /></RequireRoute>} />
                  <Route path="queue" element={<RequireRoute route="queue"><Queue /></RequireRoute>} />
                  <Route path="analytics" element={<RequireRoute route="analytics"><Analytics /></RequireRoute>} />
                  <Route path="*" element={<NotFound />} />
                </Route>
                <Route path="*" element={<main id="main" style={{ padding: 24 }}><NotFound /></main>} />
              </Routes>
            </Suspense>
          </BrowserRouter>
        </AuthProvider>
      </MetaProvider>
    </LocaleProvider>
  </StrictMode>,
);
