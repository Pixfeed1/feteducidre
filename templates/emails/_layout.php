<!DOCTYPE html>
<html lang="fr" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title><?= e($subject ?? 'Fête du Cidre') ?></title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
</head>
<body style="margin:0;padding:0;background-color:#E8E0D4;font-family:'Source Sans 3',Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%">
    <div style="width:100%;background-color:#E8E0D4;padding:24px 0">
        <!--[if mso]><table width="600" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
        <div style="max-width:600px;margin:0 auto;background:#FFFDF8;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(42,35,24,0.08)">
            <?= $content ?>
        </div>
        <!--[if mso]></td></tr></table><![endif]-->
    </div>
</body>
</html>
