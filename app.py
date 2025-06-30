<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TruthLens - AI-Powered News Verification</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0f1c;
            color: #e0e0e0;
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* Navigation */
        nav {
            background: rgba(10, 15, 28, 0.95);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(99, 102, 241, 0.3);
        }

        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 70px;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
        }

        .nav-links {
            display: flex;
            gap: 30px;
            align-items: center;
        }

        .nav-links a {
            color: #a0a0a0;
            text-decoration: none;
            transition: color 0.3s;
            font-size: 16px;
        }

        .nav-links a:hover {
            color: #6366f1;
        }

        .nav-links a.active {
            color: #6366f1;
            font-weight: 500;
        }

        /* Beta Banner */
        .beta-banner {
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            padding: 12px;
            text-align: center;
            font-size: 14px;
        }

        .beta-banner span {
            cursor: pointer;
            text-decoration: underline;
        }

        /* Hero Section */
        .hero {
            padding: 60px 20px;
            text-align: center;
            background: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
        }

        .hero h1 {
            font-size: 48px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 20px;
            color: #a0a0a0;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Container */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Input Section */
        .input-section {
            background: rgba(20, 25, 40, 0.8);
            border-radius: 20px;
            padding: 40px;
            margin: 40px auto;
            border: 1px solid rgba(99, 102, 241, 0.3);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            border-bottom: 2px solid rgba(99, 102, 241, 0.3);
        }

        .tab {
            padding: 12px 24px;
            cursor: pointer;
            border: none;
            background: none;
            color: #a0a0a0;
            font-size: 16px;
            transition: all 0.3s;
            position: relative;
        }

        .tab.active {
            color: #6366f1;
        }

        .tab.active::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 2px;
            background: #6366f1;
        }

        /* Input Group */
        .input-group {
            margin-bottom: 30px;
        }

        .input-group label {
            display: block;
            margin-bottom: 10px;
            color: #a0a0a0;
            font-size: 14px;
        }

        textarea, input[type="url"] {
            width: 100%;
            padding: 15px;
            background: rgba(30, 35, 50, 0.8);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 10px;
            color: #e0e0e0;
            font-size: 16px;
            transition: all 0.3s;
            resize: vertical;
        }

        textarea:focus, input[type="url"]:focus {
            outline: none;
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        /* Buttons */
        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
        }

        .btn-secondary {
            background: rgba(99, 102, 241, 0.2);
            color: #6366f1;
            border: 1px solid #6366f1;
        }

        .btn-secondary:hover {
            background: rgba(99, 102, 241, 0.3);
        }

        .btn-ghost {
            background: transparent;
            color: #a0a0a0;
            border: 1px solid rgba(160, 160, 160, 0.3);
        }

        .btn-ghost:hover {
            border-color: #6366f1;
            color: #6366f1;
        }

        /* Progress Bar */
        .progress-container {
            margin: 30px 0;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(99, 102, 241, 0.2);
            border-radius: 4px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            width: 0%;
            transition: width 0.3s;
            animation: shimmer 1s infinite;
        }

        @keyframes shimmer {
            0% { opacity: 0.8; }
            50% { opacity: 1; }
            100% { opacity: 0.8; }
        }

        .progress-text {
            text-align: center;
            margin-top: 10px;
            color: #a0a0a0;
            font-size: 14px;
        }

        /* Results Section */
        .results-section {
            display: none;
            margin: 40px 0;
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .result-card {
            background: rgba(20, 25, 40, 0.8);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            transition: all 0.3s;
        }

        .result-card:hover {
            border-color: #6366f1;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(99, 102, 241, 0.2);
        }

        .result-card h3 {
            color: #6366f1;
            margin-bottom: 15px;
            font-size: 18px;
        }

        .score-display {
            font-size: 36px;
            font-weight: bold;
            margin: 20px 0;
        }

        .score-high { color: #10b981; }
        .score-medium { color: #f59e0b; }
        .score-low { color: #ef4444; }

        /* Bias Spectrum */
        .bias-spectrum {
            margin: 20px 0;
            padding: 20px;
            background: rgba(30, 35, 50, 0.5);
            border-radius: 10px;
        }

        .spectrum-bar {
            height: 30px;
            background: linear-gradient(to right, #3b82f6, #6366f1, #8b5cf6, #ef4444);
            border-radius: 15px;
            position: relative;
            margin: 15px 0;
        }

        .spectrum-marker {
            position: absolute;
            top: -5px;
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 50%;
            border: 3px solid #6366f1;
            transform: translateX(-50%);
            transition: left 0.5s;
        }

        .spectrum-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 12px;
            color: #a0a0a0;
        }

        /* Tools Section */
        .tools-section {
            margin: 40px 0;
            padding: 30px;
            background: rgba(20, 25, 40, 0.6);
            border-radius: 15px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .tool-card {
            padding: 20px;
            background: rgba(30, 35, 50, 0.6);
            border-radius: 10px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            transition: all 0.3s;
        }

        .tool-card:hover {
            border-color: #6366f1;
            transform: translateY(-2px);
        }

        .tool-card i {
            font-size: 24px;
            color: #6366f1;
            margin-bottom: 10px;
        }

        .tool-card h4 {
            font-size: 16px;
            margin-bottom: 8px;
            color: #e0e0e0;
        }

        .tool-card p {
            font-size: 14px;
            color: #a0a0a0;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: rgba(20, 25, 40, 0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 90%;
            border: 1px solid rgba(99, 102, 241, 0.3);
            position: relative;
            animation: modalSlide 0.3s ease-out;
        }

        @keyframes modalSlide {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-close {
            position: absolute;
            top: 20px;
            right: 20px;
            background: none;
            border: none;
            color: #a0a0a0;
            font-size: 24px;
            cursor: pointer;
            transition: color 0.3s;
        }

        .modal-close:hover {
            color: #6366f1;
        }

        .modal h2 {
            font-size
