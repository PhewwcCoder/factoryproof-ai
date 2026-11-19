import { defineConfig } from '@playwright/test';
export default defineConfig({testDir:'./e2e',fullyParallel:false,workers:1,timeout:90000,use:{baseURL:process.env.BASE_URL||'http://127.0.0.1:3000',channel:process.env.CI?undefined:'chrome',headless:true,reducedMotion:'reduce',trace:'retain-on-failure',screenshot:'only-on-failure'},reporter:'list'});

