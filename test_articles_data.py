"""Test articles data with varying lengths and sentiments"""

TEST_ARTICLES = {
    "NVDA": [
        # Positive long article that needs chunking
        ("NVIDIA's AI Leadership Cements Future Growth", "https://test.com/nvidia-positive", 
         """NVIDIA Corporation has solidified its position as the undisputed leader in artificial intelligence computing, 
         with its latest quarterly results shattering all expectations. The company's data center revenue reached unprecedented levels, 
         driven by insatiable demand from major cloud service providers and enterprises racing to build AI infrastructure. 
         CEO Jensen Huang's strategic vision has proven remarkably prescient, as the company's early and substantial investments 
         in AI acceleration have created an almost insurmountable competitive advantage.

         The company's success extends beyond just hardware. NVIDIA's CUDA ecosystem and software development tools have created 
         a powerful moat, making it increasingly difficult for competitors to gain meaningful market share. The developer community's 
         strong preference for NVIDIA's platform has created a virtuous cycle, where more developers create tools for NVIDIA hardware, 
         attracting more users and enterprises to standardize on NVIDIA's solutions.

         In the gaming sector, NVIDIA's RTX 40 series graphics cards have set new standards for performance and energy efficiency. 
         The adoption of ray tracing technology and DLSS 3.0 has given NVIDIA a significant technological edge over competitors. 
         Market analysis indicates that despite premium pricing, demand for high-end gaming GPUs remains robust, suggesting strong 
         brand loyalty and recognition of NVIDIA's superior technology.

         The automotive sector represents another promising growth vector for NVIDIA. The company's DRIVE platform has been selected 
         by numerous leading automakers for their next-generation vehicles. As autonomous driving technology matures, NVIDIA's 
         comprehensive solution combining hardware and software positions it perfectly to capture a significant share of this 
         expanding market. Early partnerships with Mercedes-Benz and other premium automotive brands have validated NVIDIA's approach.

         Looking ahead, analysts project continued strong growth as AI adoption accelerates across industries. The company's gross margins 
         remain industry-leading, and its strong cash flow generation provides ample resources for continued R&D investment and strategic 
         acquisitions. While some investors have expressed concerns about the stock's valuation, the company's execution and market 
         position suggest significant upside potential remains."""),

        # Negative article
        ("NVIDIA Faces Growing Challenges", "https://test.com/nvidia-negative",
         """NVIDIA's dominant position in the AI chip market may be under threat as competitors ramp up their efforts and customers 
         seek alternatives. Intel's latest AI accelerators have shown promising performance metrics, while AMD's MI300 series poses 
         a credible challenge to NVIDIA's data center dominance. Several major cloud providers have announced plans to develop their 
         own custom AI chips, potentially reducing their reliance on NVIDIA's products.

         The company's gaming division faces headwinds from a saturated market and declining cryptocurrency mining demand. The high 
         prices of NVIDIA's latest GPUs have faced criticism from the gaming community, potentially impacting future sales. AMD's 
         competitive offerings at lower price points have begun to erode NVIDIA's market share in mid-range segments.

         Regulatory concerns also loom large, as governments scrutinize NVIDIA's market dominance and impose export restrictions. 
         The company's heavy exposure to the Chinese market creates significant risks as geopolitical tensions persist."""),

        # Mixed sentiment article
        ("NVIDIA's Mixed Q4 Results", "https://test.com/nvidia-mixed",
         """NVIDIA reported mixed fourth-quarter results that highlight both opportunities and challenges. While AI-related revenue 
         exceeded expectations, showing 240% year-over-year growth, the gaming segment saw a concerning 10% decline. The company's 
         automotive division also missed estimates, suggesting difficulties in monetizing this emerging opportunity.

         Gross margins improved due to the strong data center performance, but operating expenses grew faster than expected. 
         Management's conservative guidance for the next quarter disappointed some investors, though this may reflect typical 
         seasonal patterns rather than fundamental issues.""")
    ],
    "AAPL": [
        # Long positive article
        ("Apple's Ecosystem Dominance Drives Record Results", "https://test.com/apple-positive",
         """Apple Inc. has delivered another stellar quarter, showcasing the incredible strength of its ecosystem and brand. 
         iPhone sales have reached new heights, particularly in emerging markets where premium smartphone demand continues to grow. 
         The company's services division has become a powerful growth engine, with revenues exceeding expectations and margins 
         expanding. The App Store, Apple Music, and other services have created a robust recurring revenue stream that reduces 
         reliance on hardware sales cycles.

         The launch of the Vision Pro represents Apple's most ambitious new product category in years. Early reviews have been 
         overwhelmingly positive, with experts praising the device's groundbreaking technology and potential to create new 
         computing paradigms. Developer interest has surpassed expectations, with major software companies already announcing 
         innovative applications for the platform.

         Apple's commitment to privacy and security continues to resonate with consumers, creating a significant differentiator 
         in an increasingly privacy-conscious market. The company's vertical integration strategy, combining custom silicon with 
         optimized software, has resulted in industry-leading performance and energy efficiency across its product line.

         The Mac transition to Apple Silicon has been remarkably successful, driving market share gains and margin expansion 
         in the personal computer segment. The performance and efficiency advantages of M-series chips have created a compelling 
         value proposition for both consumers and professionals. Educational and enterprise adoption has accelerated, suggesting 
         sustainable long-term growth potential.

         The company's financial strength remains unmatched, with massive cash reserves and consistent free cash flow generation 
         providing flexibility for strategic investments and shareholder returns. The board's recent increase in dividend payments 
         and share buyback authorization demonstrates confidence in Apple's future prospects."""),

        # Negative article
        ("Apple's Growth Challenges Mount", "https://test.com/apple-negative",
         """Apple faces significant headwinds as smartphone market saturation and increasing competition pressure its core business. 
         iPhone sales in China have declined amid rising competition from local brands and economic challenges. The company's 
         strict App Store policies have drawn regulatory scrutiny and developer complaints, threatening its lucrative services 
         revenue stream.

         The Vision Pro's high price point and limited initial use cases may restrict its market potential. Some analysts question 
         whether the device can achieve meaningful scale or contribute significantly to Apple's bottom line. Competition in the 
         mixed reality space is intensifying, with Meta and other companies offering more affordable alternatives.

         Supply chain dependencies and geopolitical tensions create ongoing risks for Apple's manufacturing strategy. The company's 
         heavy reliance on Chinese manufacturing has become a liability as US-China relations remain strained."""),

        # Mixed sentiment article
        ("Apple's Services Growth Offsets Hardware Challenges", "https://test.com/apple-mixed",
         """Apple's latest results present a mixed picture, with services growth helping to offset challenges in hardware segments. 
         While iPhone revenue grew modestly, iPad and Mac sales declined year-over-year. The services division posted strong 
         growth, though regulatory challenges could impact future App Store revenue.

         The company's gross margins remained stable, but increasing competition and component costs may pressure profitability. 
         Management's commentary suggested cautious optimism about future quarters, while acknowledging macroeconomic uncertainties.""")
    ]
}
