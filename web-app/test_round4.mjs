#!/usr/bin/env node

/**
 * Round 4 Frontend Verification Script
 * 
 * Checks:
 * 1. All required files exist
 * 2. No obvious syntax errors in imports
 * 3. Component structure is correct
 */

import { existsSync } from 'fs';
import { readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const srcDir = join(__dirname, 'src');

const requiredFiles = [
  // Student pages
  'app/student/problems/page.tsx',
  'app/student/problems/[id]/page.tsx',
  'app/student/problems/[id]/submissions/page.tsx',
  'app/student/submissions/[id]/page.tsx',
  
  // Components
  'components/editor/CodeEditor.tsx',
  'components/submission/VerdictBadge.tsx',
  
  // Supporting files
  'lib/api.ts',
  'types/problem.ts',
  'types/submission.ts',
];

const requiredImports = {
  'app/student/problems/page.tsx': ['getProblems', 'Problem'],
  'app/student/problems/[id]/page.tsx': ['getProblem', 'submitCode', 'CodeEditor', 'VerdictBadge'],
  'app/student/problems/[id]/submissions/page.tsx': ['getSubmissions', 'VerdictBadge'],
  'app/student/submissions/[id]/page.tsx': ['getSubmission', 'VerdictBadge'],
  'components/editor/CodeEditor.tsx': ['Editor', '@monaco-editor/react'],
  'components/submission/VerdictBadge.tsx': ['Verdict'],
};

let passed = 0;
let failed = 0;

console.log('🧪 Testing Round 4 Frontend Components\n');

// Test 1: File existence
console.log('📁 Test 1: Checking file existence...');
for (const file of requiredFiles) {
  const fullPath = join(srcDir, file);
  if (existsSync(fullPath)) {
    console.log(`  ✅ ${file}`);
    passed++;
  } else {
    console.log(`  ❌ ${file} - NOT FOUND`);
    failed++;
  }
}

// Test 2: Import verification
console.log('\n📦 Test 2: Checking imports...');
for (const [file, imports] of Object.entries(requiredImports)) {
  const fullPath = join(srcDir, file);
  if (!existsSync(fullPath)) {
    console.log(`  ⏭️  ${file} - SKIPPED (file not found)`);
    continue;
  }
  
  try {
    const content = await readFile(fullPath, 'utf-8');
    let allFound = true;
    
    for (const imp of imports) {
      if (!content.includes(imp)) {
        console.log(`  ❌ ${file} - Missing import: ${imp}`);
        allFound = false;
        failed++;
      }
    }
    
    if (allFound) {
      console.log(`  ✅ ${file} - All imports present`);
      passed++;
    }
  } catch (err) {
    console.log(`  ❌ ${file} - Error reading: ${err.message}`);
    failed++;
  }
}

// Test 3: Component structure
console.log('\n🏗️  Test 3: Checking component structure...');

const componentChecks = [
  {
    file: 'components/editor/CodeEditor.tsx',
    patterns: ['export default function CodeEditor', 'language', 'onChange', 'value'],
  },
  {
    file: 'components/submission/VerdictBadge.tsx',
    patterns: ['export default function VerdictBadge', 'verdict', 'className'],
  },
  {
    file: 'app/student/problems/page.tsx',
    patterns: ['export default function', 'getProblems', 'useState', 'useEffect'],
  },
];

for (const check of componentChecks) {
  const fullPath = join(srcDir, check.file);
  if (!existsSync(fullPath)) {
    console.log(`  ⏭️  ${check.file} - SKIPPED`);
    continue;
  }
  
  try {
    const content = await readFile(fullPath, 'utf-8');
    let allFound = true;
    
    for (const pattern of check.patterns) {
      if (!content.includes(pattern)) {
        console.log(`  ❌ ${check.file} - Missing pattern: ${pattern}`);
        allFound = false;
        failed++;
      }
    }
    
    if (allFound) {
      console.log(`  ✅ ${check.file} - Structure valid`);
      passed++;
    }
  } catch (err) {
    console.log(`  ❌ ${check.file} - Error: ${err.message}`);
    failed++;
  }
}

// Summary
console.log('\n' + '='.repeat(50));
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log('='.repeat(50));

if (failed === 0) {
  console.log('\n🎉 ALL TESTS PASSED! Round 4 is ready to push.\n');
  process.exit(0);
} else {
  console.log('\n⚠️  SOME TESTS FAILED. Please fix issues before pushing.\n');
  process.exit(1);
}
