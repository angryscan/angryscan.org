<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>XML Sitemap - Angry Data Scanner</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <style type="text/css">
          body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
          }
          h1 {
            color: #1a1a1a;
            border-bottom: 3px solid #4a90e2;
            padding-bottom: 10px;
            margin-bottom: 30px;
          }
          .intro {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }
          .intro p {
            margin: 10px 0;
            color: #666;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
          }
          th {
            background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
            color: white;
            text-align: left;
            padding: 15px;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }
          td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
          }
          tr:hover {
            background-color: #f8f9fa;
          }
          tr:last-child td {
            border-bottom: none;
          }
          .url {
            color: #4a90e2;
            text-decoration: none;
            font-weight: 500;
          }
          .url:hover {
            text-decoration: underline;
            color: #357abd;
          }
          .priority {
            font-weight: 600;
            color: #28a745;
          }
          .changefreq {
            text-transform: capitalize;
            color: #6c757d;
          }
          .lastmod {
            color: #495057;
            font-family: 'Courier New', monospace;
            font-size: 13px;
          }
          .language-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 5px;
            text-transform: uppercase;
          }
          .lang-en { background: #e3f2fd; color: #1976d2; }
          .lang-ru { background: #fff3e0; color: #f57c00; }
          .lang-de { background: #f3e5f5; color: #7b1fa2; }
          .lang-es { background: #e8f5e9; color: #388e3c; }
          .lang-fr { background: #fce4ec; color: #c2185b; }
          .alternate-links {
            margin-top: 5px;
            font-size: 12px;
            color: #6c757d;
          }
          .alternate-links a {
            color: #6c757d;
            text-decoration: none;
            margin-right: 10px;
          }
          .alternate-links a:hover {
            color: #4a90e2;
            text-decoration: underline;
          }
          .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
          }
          .stat-box {
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 150px;
          }
          .stat-box strong {
            display: block;
            font-size: 24px;
            color: #4a90e2;
            margin-bottom: 5px;
          }
          .stat-box span {
            color: #666;
            font-size: 14px;
          }
        </style>
      </head>
      <body>
        <h1>XML Sitemap</h1>
        <div class="intro">
          <p>This sitemap contains <strong><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></strong> URLs from the Angry Data Scanner website.</p>
          <p>Last generated: <strong><xsl:value-of select="sitemap:urlset/sitemap:url[1]/sitemap:lastmod"/></strong></p>
        </div>
        <div class="stats">
          <div class="stat-box">
            <strong><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></strong>
            <span>Total URLs</span>
          </div>
          <div class="stat-box">
            <strong><xsl:value-of select="count(sitemap:urlset/sitemap:url[sitemap:priority='1.0'])"/></strong>
            <span>High Priority</span>
          </div>
          <div class="stat-box">
            <strong><xsl:value-of select="count(sitemap:urlset/sitemap:url[contains(sitemap:loc, '/ru/') or contains(sitemap:loc, '/de/') or contains(sitemap:loc, '/es/') or contains(sitemap:loc, '/fr/')])"/></strong>
            <span>Multilingual Pages</span>
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Language</th>
              <th>Priority</th>
              <th>Change Frequency</th>
              <th>Last Modified</th>
            </tr>
          </thead>
          <tbody>
            <xsl:for-each select="sitemap:urlset/sitemap:url">
              <xsl:sort select="sitemap:priority" order="descending"/>
              <xsl:sort select="sitemap:loc"/>
              <tr>
                <td>
                  <a class="url" href="{sitemap:loc}">
                    <xsl:value-of select="sitemap:loc"/>
                  </a>
                  <xsl:if test="html:link">
                    <div class="alternate-links">
                      <xsl:for-each select="html:link">
                        <a href="{@href}" title="Alternate language: {@hreflang}">
                          <xsl:value-of select="@hreflang"/>
                        </a>
                      </xsl:for-each>
                    </div>
                  </xsl:if>
                </td>
                <td>
                  <xsl:choose>
                    <xsl:when test="contains(sitemap:loc, '/ru/')">
                      <span class="language-badge lang-ru">RU</span>
                    </xsl:when>
                    <xsl:when test="contains(sitemap:loc, '/de/')">
                      <span class="language-badge lang-de">DE</span>
                    </xsl:when>
                    <xsl:when test="contains(sitemap:loc, '/es/')">
                      <span class="language-badge lang-es">ES</span>
                    </xsl:when>
                    <xsl:when test="contains(sitemap:loc, '/fr/')">
                      <span class="language-badge lang-fr">FR</span>
                    </xsl:when>
                    <xsl:otherwise>
                      <span class="language-badge lang-en">EN</span>
                    </xsl:otherwise>
                  </xsl:choose>
                </td>
                <td>
                  <span class="priority">
                    <xsl:value-of select="sitemap:priority"/>
                  </span>
                </td>
                <td>
                  <span class="changefreq">
                    <xsl:value-of select="sitemap:changefreq"/>
                  </span>
                </td>
                <td>
                  <span class="lastmod">
                    <xsl:value-of select="sitemap:lastmod"/>
                  </span>
                </td>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
